package main

func main() {
	cards := newDeck()
	cards.shuffle()
	hand := cards.deal2(5)
	hand.print()
	cards.print()
}
