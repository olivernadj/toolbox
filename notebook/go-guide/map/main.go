package main

import "fmt"

func main() {
	//colors := map[string]string{
	//	"red": "#ff0000",
	//	"greed": "#0000ff",
	//}

	//var colors map[string]string

	colors := make(map[string]string)
	colors["white"] = "#ffffff"
	colors["black"] = "#000000"
	fmt.Println(colors)
	delete(colors, "white")
	fmt.Println(colors)

	colors["white"] = "#ffffff"
	colors["red"] = "#ff0000"
	colors["greed"] = "#0000ff"
	printMap(colors)
}


func printMap(c map[string]string) {
	for color, hex := range c {
		fmt.Printf("k: %v v: %v\n", color, hex)
	}
}