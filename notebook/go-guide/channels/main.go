package main

import (
	"fmt"
	"net/http"
	"time"
)

func main() {

	links := []string{
		"http://google.com",
		"http://facebook.com",
		"http://stackoverflow.com",
		"http://golang.org",
		"http://amazon.com",
	}

	c := make(chan string)

	for _, link := range links {
		go checkLink(link, c)
	}

	//for i:=0; i<len(links); i++ {
	//	fmt.Println(<-c)
	//}

	//for  {
	//	go checkLink(<-c, c)
	//}

	//for l := range c {
	//	go checkLink(l, c)
	//}

	for l := range c {
		go func(l string) {
			time.Sleep(5 * time.Second)
			checkLink(l, c)
		}(l)
	}

}

func checkLink(link string, c chan string) {
	_, err := http.Get(link)
	if err != nil {
		fmt.Println(link, "might be down!")
		//time.Sleep(5 * time.Second)
		c <- link
		return
	}
	fmt.Println(link, "is up!")
	//time.Sleep(5 * time.Second)
	c <- link
}