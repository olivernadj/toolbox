package main

import "fmt"

func main() {
	for _, i := range NewSlice(0, 11, 1) {
		if i%2 == 0 {
			fmt.Printf("%v is even\n" , i)
		} else {
			fmt.Printf("%v is odd\n" , i)
		}
	}
}

func NewSlice(start, count, step int) []int {
	s := make([]int, count)
	for i := range s {
		s[i] = start
		start += step
	}
	return s
}
