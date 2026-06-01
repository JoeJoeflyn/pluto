package core

import "time"

type Expense struct {
	ID         int       `json:"id"`
	Date       time.Time `json:"date"`
	Amount     float64   `json:"amount"`
	Currency   string    `json:"currency"`
	Category   string    `json:"category"`
	Merchant   string    `json:"merchant"`
	Notes      string    `json:"notes"`
	ImagePath  string    `json:"image_path"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  time.Time `json:"updated_at"`
	SyncedAt   *time.Time `json:"synced_at"`
}

type Category struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	Icon string `json:"icon"`
}
