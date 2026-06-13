package pluto

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"time"
)

// --- API types mirroring the backend ---

type LineItem struct {
	ID         int     `json:"id"`
	OrderIndex int     `json:"order_index"`
	Name       string  `json:"name"`
	Price      float64 `json:"price"`
	Quantity   int     `json:"quantity"`
	Category   *string `json:"category"`
}

type Expense struct {
	ID             int        `json:"id"`
	Date           string     `json:"date"`
	Time           *string    `json:"time"`
	Amount         float64    `json:"amount"`
	Currency       string     `json:"currency"`
	Subtotal       *float64   `json:"subtotal"`
	Tax            *float64   `json:"tax"`
	Tip            *float64   `json:"tip"`
	Discount       *float64   `json:"discount"`
	PaymentMethod  *string    `json:"payment_method"`
	CardType       *string    `json:"card_type"`
	CardLast4      *string    `json:"card_last4"`
	Cashier        *string    `json:"cashier"`
	TransactionID  *string    `json:"transaction_id"`
	ReferenceID    *string    `json:"reference_id"`
	AuthID         *string    `json:"auth_id"`
	Address        *string    `json:"address"`
	Phone          *string    `json:"phone"`
	Email          *string    `json:"email"`
	Category       string     `json:"category"`
	Merchant       string     `json:"merchant"`
	MerchantID     *int       `json:"merchant_id"`
	Notes          string     `json:"notes"`
	ImagePath      string     `json:"image_path"`
	RawText        *string    `json:"raw_text"`
	CreatedAt      string     `json:"created_at"`
	UpdatedAt      string     `json:"updated_at"`
	SyncedAt       *string    `json:"synced_at"`
	LineItems      []LineItem `json:"line_items"`
}

type Category struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	Icon string `json:"icon"`
}

type Merchant struct {
	ID         int      `json:"id"`
	Name       string   `json:"name"`
	Address    *string  `json:"address"`
	Phone      *string  `json:"phone"`
	Email      *string  `json:"email"`
	FirstSeen  *string  `json:"first_seen"`
	LastSeen   *string  `json:"last_seen"`
	VisitCount int      `json:"visit_count"`
}

type CategoryBreakdown struct {
	Category string  `json:"category"`
	Total    float64 `json:"total"`
	Count    int     `json:"count"`
}

type Stats struct {
	Total      float64            `json:"total"`
	Count      int                `json:"count"`
	ByCategory []CategoryBreakdown `json:"by_category"`
}

type ScanExtracted struct {
	Date       string         `json:"date"`
	Amount     *float64       `json:"amount"`
	Currency   string         `json:"currency"`
	Merchant   string         `json:"merchant"`
	Address    *string        `json:"address"`
	Phone      *string        `json:"phone"`
	Category   string         `json:"category"`
	Items      []ExtractedItem `json:"items"`
	Confidence *string        `json:"confidence"`
}

type ExtractedItem struct {
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

type ScanResult struct {
	ImagePath   string         `json:"image_path"`
	Extracted   ScanExtracted  `json:"extracted"`
	Errors      []string       `json:"errors"`
	NeedsReview []string       `json:"needs_review"`
}

// --- HTTP client ---

type Client struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewClient(baseURL string) *Client {
	return &Client{
		BaseURL:    baseURL,
		HTTPClient: &http.Client{Timeout: 120 * time.Second},
	}
}

func (c *Client) do(method, path string, body any) ([]byte, error) {
	var reqBody io.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("marshal body: %w", err)
		}
		reqBody = bytes.NewReader(b)
	}

	req, err := http.NewRequest(method, c.BaseURL+path, reqBody)
	if err != nil {
		return nil, fmt.Errorf("new request: %w", err)
	}
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http do: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body: %w", err)
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API %d: %s", resp.StatusCode, string(data))
	}
	return data, nil
}

func (c *Client) Health() (string, error) {
	data, err := c.do("GET", "/health", nil)
	if err != nil {
		return "", err
	}
	var res struct {
		Status string `json:"status"`
	}
	if err := json.Unmarshal(data, &res); err != nil {
		return "", err
	}
	return res.Status, nil
}

func (c *Client) ListExpenses(category string, month, year, limit int) ([]Expense, error) {
	q := url.Values{}
	if category != "" {
		q.Set("category", category)
	}
	if month > 0 {
		q.Set("month", strconv.Itoa(month))
	}
	if year > 0 {
		q.Set("year", strconv.Itoa(year))
	}
	if limit > 0 {
		q.Set("limit", strconv.Itoa(limit))
	}
	path := "/expenses"
	if s := q.Encode(); s != "" {
		path += "?" + s
	}
	data, err := c.do("GET", path, nil)
	if err != nil {
		return nil, err
	}
	var expenses []Expense
	if err := json.Unmarshal(data, &expenses); err != nil {
		return nil, err
	}
	return expenses, nil
}

func (c *Client) GetExpense(id int) ([]Expense, error) {
	// No single-expense endpoint — fetch all and filter client-side
	expenses, err := c.ListExpenses("", 0, 0, 500)
	if err != nil {
		return nil, err
	}
	for _, e := range expenses {
		if e.ID == id {
			return []Expense{e}, nil
		}
	}
	return nil, fmt.Errorf("expense %d not found", id)
}

func (c *Client) DeleteExpense(id int) error {
	_, err := c.do("DELETE", fmt.Sprintf("/expenses/%d", id), nil)
	return err
}

func (c *Client) Stats(month, year int, categoryBreakdown bool) (*Stats, error) {
	q := url.Values{}
	if month > 0 {
		q.Set("month", strconv.Itoa(month))
	}
	if year > 0 {
		q.Set("year", strconv.Itoa(year))
	}
	if categoryBreakdown {
		q.Set("category", "true")
	}
	path := "/stats"
	if s := q.Encode(); s != "" {
		path += "?" + s
	}
	data, err := c.do("GET", path, nil)
	if err != nil {
		return nil, err
	}
	var stats Stats
	if err := json.Unmarshal(data, &stats); err != nil {
		return nil, err
	}
	return &stats, nil
}

func (c *Client) Categories() ([]Category, error) {
	data, err := c.do("GET", "/categories", nil)
	if err != nil {
		return nil, err
	}
	var cats []Category
	if err := json.Unmarshal(data, &cats); err != nil {
		return nil, err
	}
	return cats, nil
}

func (c *Client) Merchants() ([]Merchant, error) {
	data, err := c.do("GET", "/merchants", nil)
	if err != nil {
		return nil, err
	}
	var m []Merchant
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, err
	}
	return m, nil
}

func (c *Client) CreateFromScan(imagePath string, result *ScanResult) (*Expense, error) {
	type createBody struct {
		Date      string          `json:"date"`
		Amount    float64         `json:"amount"`
		Currency  string          `json:"currency"`
		Category  string          `json:"category"`
		Merchant  string          `json:"merchant"`
		ImagePath string          `json:"image_path"`
		Items     []ExtractedItem `json:"line_items"`
	}
	ext := result.Extracted
	amount := 0.0
	if ext.Amount != nil {
		amount = *ext.Amount
	}
	body := createBody{
		Date:      ext.Date,
		Amount:    amount,
		Currency:  ext.Currency,
		Category:  ext.Category,
		Merchant:  ext.Merchant,
		ImagePath: imagePath,
		Items:     ext.Items,
	}
	data, err := c.do("POST", "/expenses", body)
	if err != nil {
		return nil, err
	}
	var exp Expense
	if err := json.Unmarshal(data, &exp); err != nil {
		return nil, err
	}
	return &exp, nil
}

func (c *Client) Scan(imagePath string) (*ScanResult, error) {
	file, err := os.Open(imagePath)
	if err != nil {
		return nil, fmt.Errorf("open image: %w", err)
	}
	defer file.Close()

	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	fw, err := w.CreateFormFile("file", filepath.Base(imagePath))
	if err != nil {
		return nil, fmt.Errorf("create form file: %w", err)
	}
	if _, err := io.Copy(fw, file); err != nil {
		return nil, fmt.Errorf("copy file: %w", err)
	}
	w.Close()

	req, err := http.NewRequest("POST", c.BaseURL+"/scan", &buf)
	if err != nil {
		return nil, fmt.Errorf("new request: %w", err)
	}
	req.Header.Set("Content-Type", w.FormDataContentType())

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http do: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read body: %w", err)
	}
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API %d: %s", resp.StatusCode, string(data))
	}

	var result ScanResult
	if err := json.Unmarshal(data, &result); err != nil {
		return nil, err
	}
	return &result, nil
}
