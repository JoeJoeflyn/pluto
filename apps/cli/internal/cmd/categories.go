package cmd

import (
	"fmt"
	"os"

	pluto "github.com/giogio/pluto/cli/internal"
	"github.com/spf13/cobra"
)

var categoriesCmd = &cobra.Command{
	Use:   "categories",
	Short: "List expense categories",
	Run: func(_ *cobra.Command, _ []string) {
		c := newClient()
		cats, err := c.Categories()
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		if len(cats) == 0 {
			fmt.Println("No categories found.")
			return
		}
		t := pluto.NewTable("ID", "NAME", "ICON")
		for _, cat := range cats {
			t.AddRow(fmt.Sprintf("%d", cat.ID), cat.Name, cat.Icon)
		}
		fmt.Print(t.String())
	},
}
