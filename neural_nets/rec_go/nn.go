package main 
import (
	"encoding/csv"
	"errors"
	"fmt"
	"log"
//	"math"
	"math/rand"
	"os"
	"strconv"
	"time"


	"gonum.org/v1/gonum/floats"
	"gonum.org/v1/gonum/mat"
)



type neuralNet struct{
  config neuralNetConfig
  wHidden *mat.Dense
  bHidden *mat.Dense
  wOut *mat.Dense
  bOut *mat.Dense
}


type neuralNetConfig struct{
  inputN int 
  outputN int
  hiddenN int 
  nEpochs int
  learningRate float64
}




func main()  {
  
  var data string
  fmt.Println("Provide input file: ")
  fmt.Scanln(&data)
  // function to split data (csv or json response from api call into a training and test set)
  // return contents + train_contents
  //contents, err := os.ReadFile(data)
  
  fmt.Println("File Read Successfully")
  fmt.Println("Input values for config")
  
  var inputVal int 
  fmt.Println("Input Input Neuron: ")
  fmt.Scanln(&inputVal)
  
  var outputVal int 
  fmt.Println("Input Output Neuron: ")
  fmt.Scanln(&outputVal)
  
  var layers int 
  fmt.Println("Input number of layers: ")
  fmt.Scanln(&layers)
  
  var epochs int
  fmt.Println("Input number of epochs")
  fmt.Scanln(&epochs)
  
  var lR float64 
  fmt.Println("Input learning rate (under 1.0)")
  fmt.Scanln(&lR)

  inputs, labels := makeInputAndLabels(data)
  
  config := neuralNetConfig{
    inputN: inputVal,
    outputN: outputVal,
    hiddenN: layers,
    nEpochs: epochs,
    learningRate: lR,
  }
  
  network := newNetwork(config)
  if err := network.train(inputs, labels); err != nil {
    log.Fatal(err)
  }
  
  //training 
  testInputs, testLabels := makeInputAndLabels(data)
  predictions, err := network.predict(testInputs)
  if err != nil {
    log.Fatal(err)
  }

  //accuracy 
  var truePosNeg int 
  numPredictions, _ := predictions.Dims()
  for i := 0; i < numPredictions; i++ {
    labelRow := mat.Row(nil, i, testLabels)
    var prediction int
    for idx, label := range labelRow {
      if label == 1.0 {
        prediction = idx
        break
      }
    }

    if predictions.At(i, prediction) == floats.Max(mat.Row(nil, i, predictions)) {
      truePosNeg++
    }
  }

  accuracy := float64(truePosNeg) / float64(numPredictions)

  fmt.Printf("\nAccuracy = %0.2\n\n", accuracy)
  
}

func newNetwork(config neuralNetConfig) *neuralNet {
  return &neuralNet{config: config}
}

// training using backprop 
func (nn *neuralNet) train(x,y *mat.Dense) error {
  randSource := rand.NewSource(time.Now().UnixNano())
  randGen := rand.New(randSource)

  wHidden := mat.NewDense(nn.config.inputN, nn.config.hiddenN, nil)
  bHidden := mat.NewDense(1, nn.config.hiddenN, nil)
  wOut := mat.NewDense(nn.config.hiddenN, nn.config.outputN, nil)
  bOut := mat.NewDense(1, nn.config.outputN, nil)

  wHiddenRaw := wHidden.RawMatrix().Data
  bHiddenRaw := bHidden.RawMatrix().Data
  wOutRaw := wOut.RawMatrix().Data
  bOutRaw := bOut.RawMatrix().Data

  for _, param := range [][]float64 {
    wHiddenRaw,
    bHiddenRaw,
    wOutRaw,
    bOutRaw,
  } {
    for i := range param {
      param[i] = randGen.Float64()
    }
  }

  output := new(mat.Dense)
  if err := nn.backpropagate(x, y, wHidden, bHidden, wOut, bOut, output); err != nil {
    return err
  }

  nn.wHidden = wHidden
  nn.bHidden = bHidden
  nn.wOut = wOut
  nn.bOut = bOut

  return nil
}

//back prop method 
 func (nn *neuralNet) backpropagate(x, y, wHidden, bHidden, wOut, bOut, output *mat.Dense) error {
  for i := 0; i < nn.config.nEpochs; i++ {
    hiddenLayerInput := new(mat.Dense)
    hiddenLayerInput.Mul(x, wHidden)
    addB_hidden := func(_, col int, v float64) float64 { return v + bHidden.At(0, col)}
    hiddenLayerInput.Apply(addB_hidden, hiddenLayerInput)

    hiddenLayerActivation := new(mat.Dense)
    applyActivationFunction := func(_,_ int, v float64) float64 {return ReLU(v)}
    hiddenLayerActivation.Apply(applyActivationFunction, hiddenLayerInput)

    outputLayerInput := new(mat.Dense)
    outputLayerInput.Mul(hiddenLayerActivation, wOut)
    addB_out := func(_, col int, v float64) float64 { return v + bOut.At(0,col)}
    outputLayerInput.Apply(addB_out, outputLayerInput)
    output.Apply(applyActivationFunction, outputLayerInput)

    networkError := new(mat.Dense)
    networkError.Sub(y, output)

    slopeOutputLayer := new(mat.Dense)
    applyActivationPrime := func(_, _ int, v float64) float64 {return ReLUprime(v)}
    slopeHiddenLayer := new(mat.Dense)
    slopeHiddenLayer.Apply(applyActivationPrime, hiddenLayerActivation)

    dOutput := new(mat.Dense)
    dOutput.MulElem(networkError, slopeOutputLayer)
    errorAtHidden := new(mat.Dense)
    errorAtHidden.Mul(dOutput, wOut.T())

    dHiddenLayer := new(mat.Dense)
    dHiddenLayer.MulElem(errorAtHidden, slopeHiddenLayer)

    wOutAdj := new(mat.Dense)
    wOutAdj.Mul(hiddenLayerActivation.T(), dOutput)
    wOutAdj.Scale(nn.config.learningRate, wOutAdj)
    wOut.Add(wOut, wOutAdj)

    bOutAdj, err := sumAxis(0, dOutput)
    if err != nil {
      return err
    }
    bOutAdj.Scale(nn.config.learningRate, bOutAdj)
    bOut.Add(bOut, bOutAdj)

    wHiddenAdj := new(mat.Dense)
    wHiddenAdj.Mul(x.T(), dHiddenLayer)
    wHiddenAdj.Scale(nn.config.learningRate, wHiddenAdj)
    wHidden.Add(wHidden, wHiddenAdj)

    bHiddenAdj, err := sumAxis(0, dHiddenLayer)
    if err != nil {
      return err
    }

    bHiddenAdj.Scale(nn.config.learningRate, bHiddenAdj)
    bHidden.Add(bHidden, bHiddenAdj)
  }
  return nil

}

func (nn *neuralNet) predict(x *mat.Dense) (*mat.Dense, error) {
  if nn.wHidden == nil || nn.wOut == nil {
    return nil, errors.New("Weights are empty")
  }
  if nn.bHidden == nil || nn.bOut == nil {
    return nil, errors.New("Biases are empty")
  }
  

  output := new(mat.Dense)
  //feed forward 
  hiddenLayerInput := new(mat.Dense)
  hiddenLayerInput.Mul(x, nn.wHidden)
  addB_hidden := func (_, col int, v float64) float64 {return v + nn.bHidden.At(0,col)}
  hiddenLayerInput.Apply(addB_hidden, hiddenLayerInput)

  hiddenLayerActivations := new(mat.Dense)
  applyActivation := func (_, _ int, v float64) float64 {
    return ReLU(v)
  }
  hiddenLayerActivations.Apply(applyActivation, hiddenLayerInput)

  outputLayerInput := new(mat.Dense)
  outputLayerInput.Mul(hiddenLayerActivations, nn.wOut)
  addB_out := func(_, col int, v float64) float64 { return v + nn.bOut.At(0, col) }
  outputLayerInput.Apply(addB_out, outputLayerInput)
  output.Apply(applyActivation, outputLayerInput)

  return output, nil 
}


// ReLU activation function
func ReLU(x float64) float64 {
    if x > 0 {
        return x
    }
    return 0
}

// ReLU prime (derivative of ReLU)
func ReLUprime(x float64) float64 {
    if x > 0 {
        return 1
    }
    return 0
}

func sumAxis(axis int, m *mat.Dense) (*mat.Dense, error) {
  nRows, nCols := m.Dims()
  var output *mat.Dense

  switch axis {
  case 0:
  data := make([]float64, nCols)
  for i := 0; i < nCols; i++ {
      col := mat.Col(nil, i, m)
      data[i] = floats.Sum(col)
    }
  output = mat.NewDense(1, nCols, data)
  
  case 1: 
  data := make([]float64, nRows)
  for i := 0; i < nRows; i++ {
      row := mat.Row(nil, i, m)
      data[i] = floats.Sum(row)
    }
  output = mat.NewDense(nRows, 1, data)
  
  default: 
    return nil, errors.New("invalid axis, must be 0 or 1")
  }
  return output, nil
}

//variable header length
func getCSVHeaderLength(filePath string) (int, error) {
  file, err := os.Open(filePath)
  if err != nil {
    return 0, err
  }
  defer file.Close()
  reader := csv.NewReader(file)

  header, err := reader.Read()
  if err != nil {
    return 0, err
  }

  return len(header), nil
}



func makeInputAndLabels(fileName string) (*mat.Dense, *mat.Dense) {
    f, err := os.Open(fileName)
    if err != nil {
        log.Fatal(err)
    }
    defer f.Close()

    reader := csv.NewReader(f)
    header, err := reader.Read() // Reading header
    if err != nil {
        log.Fatal(err)
    }

    numLabelColumns := len(header) // All columns are labels

    rawCSVData, err := reader.ReadAll()
    if err != nil {
        log.Fatal(err)
    }

    // Since all columns are labels, there are no input features.
    labelsData := make([]float64, numLabelColumns*(len(rawCSVData)-1))

    var labelsIndex int

    for idx, record := range rawCSVData {
        if idx == 0 { // Skip header
            continue
        }

        for _, val := range record {
            parsedVal, err := strconv.ParseFloat(val, 64)
            if err != nil {
                log.Fatal(err)
            }

            labelsData[labelsIndex] = parsedVal
            labelsIndex++
        }
    }

    // Creating an empty matrix for inputs as there are no input features
    inputs := mat.NewDense(len(rawCSVData)-1, 0, nil)
    // Creating the labels matrix
    labels := mat.NewDense(len(rawCSVData)-1, numLabelColumns, labelsData)
    return inputs, labels
}
