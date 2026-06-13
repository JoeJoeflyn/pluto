package cmd

import (
	"fmt"
	"os"

	pluto "github.com/giogio/pluto/cli/internal"
	"github.com/spf13/cobra"
)

var (
	listCategory string
	listMonth    int
	listYear     int
	listLimit    int
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List expenses",
	Run: func(_ *cobra.Command, _ []string) {
		c := newClient()
		expenses, err := c.ListExpenses(listCategory, listMonth, listYear, listLimit)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		if len(expenses) == 0 {
			fmt.Println("No expenses found.")
			return
		}
		t := pluto.NewTable("ID", "DATE", "AMOUNT", "CURRENCY", "MERCHANT", "CATEGORY")
		for _, e := range expenses {
			t.AddRow(
				fmt.Sprintf("%d", e.ID),
				e.Date,
				fmt.Sprintf("%.2f", e.Amount),
				e.Currency,
				e.Merchant,
				e.Category,
			)
		}
		fmt.Print(t.String())
	},
}

func init() {
	listCmd.Flags().StringVarP(&listCategory, "category", "c", "", "Filter by category")
	listCmd.Flags().IntVarP(&listMonth, "month", "m", 0, "Filter by month (1-12)")
	listCmd.Flags().IntVarP(&listYear, "year", "y", 0, "Filter by year (e.g. 2026)")
	listCmd.Flags().IntVarP(&listLimit, "limit", "l", 50, "Max results (max 500)")
}
