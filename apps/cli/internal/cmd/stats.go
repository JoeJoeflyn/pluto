package cmd

import (
	"fmt"
	"os"

	pluto "github.com/giogio/pluto/cli/internal"
	"github.com/spf13/cobra"
)

var (
	statsMonth    int
	statsYear     int
	statsCategory bool
)

var statsCmd = &cobra.Command{
	Use:   "stats",
	Short: "Show spending statistics",
	Run: func(_ *cobra.Command, _ []string) {
		c := newClient()
		s, err := c.Stats(statsMonth, statsYear, statsCategory)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Total: %.2f\n", s.Total)
		fmt.Printf("Count: %d\n", s.Count)
		if s.Count > 0 {
			fmt.Printf("Mean:  %.2f\n", s.Total/float64(s.Count))
		}
		if len(s.ByCategory) > 0 {
			fmt.Println("\nBy category:")
			t := pluto.NewTable("CATEGORY", "TOTAL", "COUNT")
			for _, b := range s.ByCategory {
				t.AddRow(b.Category, fmt.Sprintf("%.2f", b.Total), fmt.Sprintf("%d", b.Count))
			}
			fmt.Print(t.String())
		}
	},
}

func init() {
	statsCmd.Flags().IntVarP(&statsMonth, "month", "m", 0, "Filter by month (1-12)")
	statsCmd.Flags().IntVarP(&statsYear, "year", "y", 0, "Filter by year (e.g. 2026)")
	statsCmd.Flags().BoolVarP(&statsCategory, "category", "c", false, "Show per-category breakdown")
}
