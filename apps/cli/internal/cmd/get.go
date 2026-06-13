package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var getCmd = &cobra.Command{
	Use:   "get <id>",
	Short: "Show expense details",
	Args:  cobra.ExactArgs(1),
	Run: func(_ *cobra.Command, args []string) {
		c := newClient()
		results, err := c.GetExpense(atoi(args[0]))
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		if len(results) == 0 {
			fmt.Printf("Expense %s not found.\n", args[0])
			return
		}
		e := results[0]
		fmt.Printf("ID:       %d\n", e.ID)
		fmt.Printf("Date:     %s\n", e.Date)
		if e.Time != nil {
			fmt.Printf("Time:     %s\n", *e.Time)
		}
		fmt.Printf("Amount:   %.2f %s\n", e.Amount, e.Currency)
		fmt.Printf("Merchant: %s\n", e.Merchant)
		fmt.Printf("Category: %s\n", e.Category)
		if e.Subtotal != nil {
			fmt.Printf("Subtotal: %.2f\n", *e.Subtotal)
		}
		if e.Tax != nil {
			fmt.Printf("Tax:      %.2f\n", *e.Tax)
		}
		if e.Tip != nil {
			fmt.Printf("Tip:      %.2f\n", *e.Tip)
		}
		if e.Address != nil {
			fmt.Printf("Address:  %s\n", *e.Address)
		}
		if e.Notes != "" {
			fmt.Printf("Notes:    %s\n", e.Notes)
		}
		if len(e.LineItems) > 0 {
			fmt.Println("\nLine items:")
			for _, li := range e.LineItems {
				fmt.Printf("  %s x%d — %.2f\n", li.Name, li.Quantity, li.Price)
			}
		}
	},
}
