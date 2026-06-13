package pluto

import (
	"fmt"
	"strings"

	"github.com/mattn/go-runewidth"
)

func displayWidth(s string) int {
	return runewidth.StringWidth(s)
}

type Table struct {
	headers []string
	rows    [][]string
	widths  []int
}

func NewTable(headers ...string) *Table {
	t := &Table{headers: headers, widths: make([]int, len(headers))}
	for i, h := range headers {
		t.widths[i] = displayWidth(h)
	}
	return t
}

func (t *Table) AddRow(cols ...string) {
	t.rows = append(t.rows, cols)
	for i, c := range cols {
		if i < len(t.widths) && displayWidth(c) > t.widths[i] {
			t.widths[i] = displayWidth(c)
		}
	}
}

func (t *Table) pad(s string, w int) string {
	dw := displayWidth(s)
	if dw >= w {
		return s
	}
	return s + strings.Repeat(" ", w-dw)
}

func (t *Table) line(left, sep, join, right string) string {
	var b strings.Builder
	b.WriteString(left)
	for i, w := range t.widths {
		if i > 0 {
			b.WriteString(sep)
		}
		b.WriteString(strings.Repeat("─", w+2))
	}
	b.WriteString(right)
	return b.String()
}

func (t *Table) dataRow(cols []string, left, sep, right string) string {
	var b strings.Builder
	b.WriteString(left)
	for i, c := range cols {
		if i > 0 {
			b.WriteString(sep)
		}
		if i < len(t.widths) {
			b.WriteString(fmt.Sprintf(" %s ", t.pad(c, t.widths[i])))
		}
	}
	b.WriteString(right)
	return b.String()
}

func (t *Table) String() string {
	var b strings.Builder
	// top border
	b.WriteString(t.line("┌", "┬", "┬", "┐"))
	b.WriteString("\n")

	// header row
	b.WriteString(t.dataRow(t.headers, "│", "│", "│"))
	b.WriteString("\n")

	// separator
	if len(t.rows) > 0 {
		b.WriteString(t.line("├", "┼", "┼", "┤"))
		b.WriteString("\n")
	}

	// data rows
	for _, row := range t.rows {
		b.WriteString(t.dataRow(row, "│", "│", "│"))
		b.WriteString("\n")
	}

	// bottom border
	b.WriteString(t.line("└", "┴", "┴", "┘"))
	b.WriteString("\n")
	return b.String()
}
