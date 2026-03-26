# Chapter Four - Implementation & Results


## 4.1 Beam Design Implementation

The beam design module was developed using Python functions to compute structural parameters.

<p align="center">
    <a href="images/Screenshot_2049.png">
        <img src="images/Screenshot_2049.png" alt="Beam design testing result" width="500"/>
    </a>
</p>
<!-- [![Beam design testing result](images/Screenshot_2049.png)](images/Screenshot_2049.png) -->
 
The bending moment for a simply supported beam under uniformly distributed load was calculated using the formula:

Mu = wL² / 8

Where:

- w = load (kN/m)
- L = span (m)

The required steel area was computed using standard reinforcement concrete design equations.


## 4.2 Dataset Generation

A dataset was generated using simulated structural parameters to train the AI model.

<div class="span">
<p>
    <a href="images/Screenshot_2051.png.png">
        <img src="images/Screenshot_2051.png" alt="Dataset generation script" width="300"/>
    </a>
</p>
<!-- [![Dataset generation script](images/Screenshot_2051.png)](images/Screenshot_2051.png) -->

<p>
    <a href="images/Screenshot_2052.png">
        <img src="images/Screenshot_2052.png.png" alt="Dataset generation terminal print" width="300"/>
    </a>
</p>
</div>
<!-- [![Dataset generation terminal print](images/Screenshot_2052.png)](images/Screenshot_2052.png) -->

The parameters included:

- Beam span (3m – 10m)
- Load (10 kN/m – 50 kN/m)
- fck (concrete grade 20 - 30)
- fy (steel grade 500)

For each generated input, the corresponding steel area was calculated using the standard beam design equations.

A total of 5000 data samples were generated and stored in a CSV file for training purposes.

<p align="left">
    <a href="images/Screenshot_2057.png.png">
        <img src="images/Screenshot_2057.png" alt="Generated data samples in csv" width="300"/>
    </a>
</p>
<!-- [![Generated data samples in csv](images/Screenshot_2057.png)](images/Screenshot_2057.png) -->

<p align="right">
    <a href="images/Screenshot_2058.png.png">
        <img src="images/Screenshot_2056.png" alt="Generated data samples in csv" width="300"/>
    </a>
</p>
<!-- [![Generated data samples in csv](images/Screenshot_2058.png)](images/Screenshot_2058.png) -->
