package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var (
	scanCreate  bool
	scanConfirm bool
)

var scanCmd = &cobra.Command{
	Use:   "scan <image>",
	Short: "Scan a receipt image",
	Long: `Upload a receipt image to the AI backend and return extracted fields.

With --create, the extracted expense is saved to the database immediately.
With --confirm, you can review and approve the extraction interactively.`,
	Args: cobra.ExactArgs(1),
	Run: func(_ *cobra.Command, args []string) {
		c := newClient()
		result, err := c.Scan(args[0])
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}

		if len(result.Errors) > 0 {
			fmt.Println("Errors:")
			for _, e := range result.Errors {
				fmt.Printf("  - %s\n", e)
			}
		}

		ext := result.Extracted
		fmt.Println("\nExtracted fields:")
		fmt.Printf("  Date:     %s\n", nullStr(ext.Date))
		fmt.Printf("  Amount:   %s\n", nullF64(ext.Amount))
		fmt.Printf("  Currency: %s\n", ext.Currency)
		fmt.Printf("  Merchant: %s\n", nullStr(ext.Merchant))
		fmt.Printf("  Category: %s\n", ext.Category)
		if ext.Address != nil {
			fmt.Printf("  Address:  %s\n", *ext.Address)
		}
		if ext.Phone != nil {
			fmt.Printf("  Phone:    %s\n", *ext.Phone)
		}
		if len(ext.Items) > 0 {
			fmt.Println("\n  Line items:")
			for _, it := range ext.Items {
				fmt.Printf("    %s — %.2f\n", it.Name, it.Price)
			}
		}
		if len(result.NeedsReview) > 0 {
			fmt.Printf("\n  Needs review: %v\n", result.NeedsReview)
		}

		if scanCreate && len(result.Errors) == 0 {
			exp, err := c.CreateFromScan(args[0], result)
			if err != nil {
				fmt.Fprintf(os.Stderr, "\nerror saving expense: %v\n", err)
				os.Exit(1)
			}
			fmt.Printf("\nExpense created: ID %d (%.2f %s at %s)\n", exp.ID, exp.Amount, exp.Currency, exp.Merchant)
		}
	},
}

func nullStr(s string) string {
	if s == "" {
		return "-"
	}
	return s
}

func nullF64(v *float64) string {
	if v == nil {
		return "-"
	}
	return fmt.Sprintf("%.2f", *v)
}

func init() {
	scanCmd.Flags().BoolVarP(&scanCreate, "create", "C", false, "Save the extracted expense to the database")
}
