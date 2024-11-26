
# **Fuel and Natural Gas Price Visualization Tool**

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green) ![Data-Visualization](https://img.shields.io/badge/Data%20Visualization-Matplotlib-orange)  

This project provides a graphical user interface (GUI) for visualizing and comparing historical fuel and natural gas prices. With a dataset spanning from August 2000 to the present, this tool allows users to analyze trends and make data-driven insights.

## **Features**
- 📈 **Data Visualization**: Compare price trends of various commodities such as crude oil, natural gas, and heating oil.
- 🎛️ **Interactive Interface**: User-friendly controls to filter data by date, commodity, and chart type.
- 🔄 **Data Cleaning**: Automatic normalization and preparation of input datasets.
- 🔍 **Custom Comparisons**: Simultaneously visualize two different commodities for comparative analysis.
- 📊 **Multiple Plot Configurations**: Choose between single or dual plots in horizontal or vertical layouts.

## **Getting Started**
### **Prerequisites**
Ensure you have the following installed on your system:
- Python 3.8+
- Required Python libraries:
  ```bash
  pip install pandas matplotlib tk tkcalendar
  ```

### **Dataset**
The dataset used in this project is sourced from Kaggle:  
[Fuels Futures Data](https://www.kaggle.com/datasets/guillemservera/fuels-futures-data)

Download the dataset and ensure it's in the required CSV format for compatibility.

### **Running the Application**
1. Clone this repository:
   ```bash
   git clone git@github.com:whellcome/all_fuels_viz.git
   ```
2. Navigate to the project directory:
   ```bash
   cd fuel-price-visualization
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## **How It Works**
### **Key Components**
1. **Tkinter-based GUI**: Provides an intuitive interface for users to interact with data.
2. **Matplotlib Integration**: Powers the chart rendering within the application.
3. **Data Processing**: Built-in functions for cleaning, normalizing, and filtering data.

### **Workflow**
1. Load a dataset via the "File Open" button.
2. Select the commodity and date range for analysis.
3. Customize the plot layout and compare different commodities.
4. View and analyze the trends in real-time.

## **Screenshots**
![Screenshot of GUI](/data/all_fuels_viz_scr_00.jpg)  
*Example: Comparison of Natural Gas and Crude Oil Prices*

## **Planned Features**
- Integration with real-time data APIs for live updates.
- Advanced statistical analysis tools.
- Export options for generated charts.

## **Contributing**
Contributions are welcome! Please feel free to fork this repository and submit pull requests with improvements.

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Acknowledgments**
- Dataset sourced from Kaggle ([Fuels Futures Data](https://www.kaggle.com/datasets/guillemservera/fuels-futures-data)).
- Built using Python's Tkinter and Matplotlib libraries.
