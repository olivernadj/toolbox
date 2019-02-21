package main

import (
	"flag"
	"fmt"
	"math"
	"reflect"
)

type geometricShape interface {
	getArea() float64
}

type triangle struct {
	height float64
	base float64
}
type square struct {
	sideLength float64
}

func main() {
	hasTriangle := flag.Bool("triangle", false, "For triangle calculations")
	height := flag.Float64("height", 0.0, "Height of triangle")
	base := flag.Float64("base", 0.0, "Base of triangle")
	hasSquare := flag.Bool("square", false, "For square calculations")
	sideLength := flag.Float64("side", 0.0, "Side length of square")
	flag.Parse()
	if *hasTriangle {
		t := triangle{height:*height, base:*base}
		printArea(t)
	}
	if *hasSquare {
		t := square{sideLength:*sideLength}
		printArea(t)
	}
}

func printArea(gs geometricShape) {
	fmt.Println("The area of", reflect.TypeOf(gs).Name(), "is", gs.getArea())
}

func (t triangle) getArea() float64 {
	return 0.5 * t.base * t.height
}

func (s square) getArea() float64 {
	return math.Pow(s.sideLength, 2)
}