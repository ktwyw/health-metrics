# Health Metrics Calculator

Enter your weight, height, age and sex and get three numbers back: body mass
index (BMI), estimated basal metabolic rate (BMR) and a daily water target.
It comes in two versions with identical logic and the same dark palette:

- `health_gui.py` — a desktop app built with tkinter (Python 3, no
  extra packages)
- `index.html` — a web page in plain HTML, CSS and JavaScript.
  Live at https://ktwyw.github.io/health-metrics/

## Run the desktop version

```
python health_gui.py
```

tkinter ships with Python on Windows and macOS. On some Linux distributions
it's a separate package, e.g. `sudo apt install python3-tk`.

## Run the web version

Open `index.html` in a browser, or use the live link above.

## How the numbers are calculated

| Metric | Formula |
| --- | --- |
| BMI | weight (kg) ÷ height (m)² |
| BMR | Mifflin-St Jeor: 10 × weight + 6.25 × height (cm) − 5 × age, then +5 for men or −161 for women |
| Water target | 33 ml per kg of body weight |

BMI categories follow the usual cut-offs: under 18.5 underweight, 18.5–25
normal, 25–30 overweight, 30 and above obese. Height can be typed in metres
(1.75) or centimetres (175); the app converts.

These are general-population estimates and not medical advice. BMI in
particular doesn't account for muscle mass, age or body composition, so treat
the result as a rough guide rather than a verdict.

## What the code covers

Functions, type conversion, `if/elif/else`, f-strings and error handling in
Python; the same ideas in JavaScript plus DOM updates and CSS variables. The
calculation functions (`compute` and `bmi_category`) are kept separate from
the interface in both versions so they're easy to test or reuse.

## Ideas for next steps

- Add a unit toggle (lb / ft-in)
- Show the healthy weight range for the entered height
- Add an activity-level selector to turn BMR into total daily energy
- Save the last inputs so they're pre-filled next time
