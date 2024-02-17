package main 
import (
  "fmt"
  //"github.com/gocolly/colly"
  "strings"
  "os"
  "bufio"

)

func main()  {
  //c := colly.NewCollector()
  base := "https://www.statmuse.com/"
  sport_prompt := "Input sport: NBA, NFL, EPL, NHL, MLB"
  fmt.Println(sport_prompt)
  var sport string
  fmt.Scanln(&sport)
  question_prompt := "Input Question: "
  arr := make([]string, 0)
    scanner := bufio.NewScanner(os.Stdin)
    for {
        fmt.Print(question_prompt)
        // Scans a line from Stdin(Console)
        scanner.Scan()
        // Holds the string that scanned
        text := scanner.Text()
        if len(text) != 0 {
            text = strings.Replace(text, " ", "-", -1)
            arr = append(arr, text)
        } else {
            break
        }

    }
    // Use collected inputs
    fmt.Println(arr)
  //question = strings.Replace(arr, " ", "-",-1)
  //fmt.Println(question)
  combinedString := strings.Join(arr, "-")
  var url string 
  url = base + sport + "/ask/" + combinedString

  fmt.Println(url)
  //c.Visit(url)
}
