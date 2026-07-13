# Forest Fire Simulator

<img src="icon.ico" width="128" height="128" alt="scrcpy" align="right" />

A program that provides an introduction to the use of cellular automata as an approach to solving real-world problems.

## Requirements

* `python3`
* `numpy`
* `matplotlib`
* `scipy`

## Usage

Run the program:

```bash
python main.py
```

Simulation params available in graphical interface:

* **Начальное число ГСЧ** — Initial RNG Seed
* **Размер сетки деревьев** — Grid Dimensions
* **Начальное заполнение деревьями** — Initial Tree Density
* **Начальное количество горящих деревьев** — Initial Burning Trees Count
* **Частота роста деревьев** — Tree Growth Rate
* **Частота возникновения пожара** — Lightning Strike Probability
* **Длительность моделирования** — Simulation Duration
* **Представление границы** — Boundary Conditions
* **Окрестность** — Neighborhood Type

## Example output

![Example output](res.gif)
