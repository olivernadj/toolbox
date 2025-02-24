package main

import (
	"fmt"
	"html/template"
	"log"
	"os"

	"github.com/Masterminds/sprig/v3"
	"gopkg.in/yaml.v3"
)

// loadYAML loads YAML data from a given file
func loadYAML(filePath string) (map[string]interface{}, error) {
	file, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var data map[string]interface{}
	err = yaml.Unmarshal(file, &data)
	if err != nil {
		return nil, err
	}

	return data, nil
}

// renderTemplate loads and executes the template
func renderTemplate(templatePath string, values map[string]interface{}) error {
	// Read template file
	templateContent, err := os.ReadFile(templatePath)
	if err != nil {
		return err
	}

	// Parse the template
	tmpl, err := template.New("template").Funcs(sprig.FuncMap()).Parse(string(templateContent))
	if err != nil {
		return err
	}

	// Execute the template with values
	err = tmpl.Execute(os.Stdout, values)
	if err != nil {
		return err
	}

	return nil
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("Usage: go-template-renderer <template-file> <values.yaml>")
		os.Exit(1)
	}

	templatePath := os.Args[1]
	valuesPath := os.Args[2]

	// Load values.yaml
	values, err := loadYAML(valuesPath)
	if err != nil {
		log.Fatalf("Error loading YAML file: %v\n", err)
	}

	// Render template
	err = renderTemplate(templatePath, values)
	if err != nil {
		log.Fatalf("Error rendering template: %v\n", err)
	}
}
