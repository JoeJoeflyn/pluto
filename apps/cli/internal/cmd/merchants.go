package cmd

import (
	"fmt"
	"os"

	pluto "github.com/giogio/pluto/cli/internal"
	"github.com/spf13/cobra"
)

var merchantsCmd = &cobra.Command{
	Use:   "merchants",
	Short: "List merchants",
	Run: func(_ *cobra.Command, _ []string) {
		c := newClient()
		merchants, err := c.Merchants()
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		if len(merchants) == 0 {
			fmt.Println("No merchants found.")
			return
		}
		t := pluto.NewTable("ID", "NAME", "VISITS", "LAST SEEN")
		for _, m := range merchants {
			last := "-"
			if m.LastSeen != nil {
				last = *m.LastSeen
			}
			t.AddRow(fmt.Sprintf("%d", m.ID), m.Name, fmt.Sprintf("%d", m.VisitCount), last)
		}
		fmt.Print(t.String())
	},
}
