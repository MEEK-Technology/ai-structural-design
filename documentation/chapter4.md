# Chapter Four - Implementation & Results


## 4.1 Beam Design Implementation

The beam design module was developed using Python functions to compute structural parameters.

<p align="center">
    <a href="images/Screenshot_2049.png">
        <img src="images/Screenshot_2049.png" alt="Beam design testing result" width="500"/>
    </a>
    <br/>
    <em>Figure 4.1a: Beam design testing result</em>
</p>
<!-- [![Beam design testing result](images/Screenshot_2049.png)](images/Screenshot_2049.png) -->
 
The bending moment for a simply supported beam under uniformly distributed load was calculated using the formula:

Mu = wL² / 8

Where:

- w = load (kN/m)
- L = span (m)

The required steel area was computed using standard reinforcement concrete design equations.

<p align="center">
    <a href="images/Screenshot_2060.png">
        <img src="images/Screenshot_2060.png" alt="Beam design testing code" width="500"/>
    </a>
    <br/>
    <em>Figure 4.1b: Beam design testing code</em>
</p>


## 4.2 Dataset Generation

A dataset was generated using simulated structural parameters to train the AI model.

<p align="center">
    <a href="images/Screenshot_2065.png">
        <img src="images/Screenshot_2065.png" alt="Dataset generation script" width="500" />
    </a>
        <br/>
        <em>Figure 4.2a: Dataset generation script</em>
</p>

<p align="center">
    <a href="images/Screenshot_2066.png">
        <img src="images/Screenshot_2066.png" alt="Dataset generation terminal print" width="500" />
    </a>
    <br/>
    <em>Figure 4.2b: Dataset generation terminal print</em>
</p>

The parameters included:

- Beam span (3m – 10m)
- Load (10 kN/m – 50 kN/m)
- fck (concrete grade 20, 25, 30)
- fy (steel grade 460)

For each generated input, the corresponding steel area was calculated using the standard beam design equations.

A total of 5000 data samples were generated and stored in a CSV file for training purposes.

<p align="center">
    <p align="center">
        <a href="images/Screenshot_2067.png">
            <img src="images/Screenshot_2067.png" alt="Generated data samples in csv" width="45%" />
        </a>
        <br/>
        <em>Figure 4.2c: Generated data samples in csv</em>
    </p>
    <p align="center">
        <a href="images/Screenshot_2068.png">
            <img src="images/Screenshot_2068.png" alt="Generated data samples in csv" width="45%" />
        </a>
        <br/>
        <em>Figure 4.2d: Generated data samples in csv</em>
    </p>
</p>


## 4.3 AI Model Development

A machine learning model was developed to predict the required steel area for beam design based on input parameters.

<p align="center">
    <a href="images/Screenshot_2061.png">
        <img src="images/Screenshot_2061.png" alt="AI model development script" width="500" />
    </a>
    <br/>
    <em>Figure 4.3a: AI model development script</em>
</p>

The dataset generated was used to train the model, with the following features:

- Span
- Load
- fck
- fy

The target output was:

- Steel area

A Random Forest Regression algorithm was used for training due to its ability to handle nonlinear relationships and provide accurate predictions.

<p align="center">
    <a href="images/Screenshot_2062.png">
        <img src="images/Screenshot_2062.png" alt="trained AI model" width="500" />
    </a>
    <br/>
    <em>Figure 4.3b: trained AI model</em>
</p>

The trained model was saved as "model.pkl" and used for making predictions within the system.

The result output from the model was compared with the calculated steel area from the beam design module to evaluate the accuracy of predictions.

<p align="center">
    <a href="images/Screenshot_2069.png">
        <img src="images/Screenshot_2069.png" alt="AI generated Steel Area result" width="500" />
    </a>
    <br/>
    <em>Figure 4.3c: AI generated Steel Area result</em>
</p>


## 4.4 Model Input Features

The AI model was trained using four input features:

- Span
- Load
- Concrete strength/grade (fck)
- Steel strength/grade (fy)

These parameters were used to improve the accuracy of predictions and better reflect real-world structural design conditions.

The inclusion of both concrete and steel grades allowed the model to learn the influence of material properties on the required steel area for beam design.

<p align="center">
    <a href="images/Screenshot_2071.png">
        <img src="images/Screenshot_2071.png" alt="Model input features" width="500" />
    </a>
    <br/>
    <em>Figure 4.4a: Model input features</em>
</p>

