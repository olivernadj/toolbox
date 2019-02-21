package main

import "fmt"

type contactInfo struct {
	email string
	zipCode int
}


type person struct {
	firstName string
	lastName string
	contactInfo
}


func main() {
	////alex := person{ firstName:"Alex", lastName:"Anderson"}
	//var alex person
	//alex.firstName = "Alex"
	//alex.lastName = "Anderson"
	//fmt.Println(alex)
	//fmt.Printf("%+v\n ", alex)

	jim := person{
		firstName:"Jim",
		lastName:"Party",
		contactInfo: contactInfo{
			email: "jim@example.com",
			zipCode: 94000,
		},
	}
	//(&jim).updateName("Bello")
	jim.updateName("Bello")
	jim.print()
}

func (p *person) updateName(newFirstName string)  {
	(*p).firstName = newFirstName
}

func (p person) print() {
	fmt.Printf("%+v", p)
}

