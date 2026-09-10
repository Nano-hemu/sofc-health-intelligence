# Mathematics notes

These notes are written as an interview study guide and map directly to the implementation.

## 1. Two time axes

Let (i) identify a cell, (k) its degradation assessment, and (t) a sample inside that
assessment. A raw observation is

\[
\mathbf{x}_{i,k,t} = [V_{i,k,t}, j_{i,k,t}, Z_{i,k,t}, \ldots].
\]

The fast axis (t) describes a curve or transient experiment. The slow axis (k) describes
degradation. Treating every row as a single equally spaced series discards this hierarchy and
creates invalid temporal relationships at file boundaries.

## 2. Autocorrelation and effective information

For a weakly stationary scalar series (y_t), lag-(h) autocorrelation is

\[
\rho(h)=\frac{\operatorname{Cov}(y_t,y_{t-h})}{\operatorname{Var}(y_t)}.
\]

Large adjacent autocorrelation means that 100,000 rows do not provide 100,000 independent examples.
This is why the number of cells and independent degradation trajectories matters more than the raw
row count when claiming generalization.

## 3. Candidate state-of-health definition

A transparent candidate based on an IV curve is current retention at a reference voltage:

\[
SOH^{(j)}_{i,k}=\frac{|j_{i,k}(V_{ref})|}{|j_{i,1}(V_{ref})|}.
\]

The current density is interpolated because the measured voltage grid differs slightly between
assessments. This candidate must be tested against maximum-power retention, voltage at a reference
current, and resistance-based indicators before it becomes the target.

## 4. Forecasting statement

At assessment (k), an (h)-step model estimates

\[
p\!\left(SOH_{i,k+h}\mid\mathbf{x}_{i,1:k}\right).
\]

A point forecast provides only the conditional centre. A decision-grade prognostic model also
estimates uncertainty and derives RUL as a first-passage time through an end-of-life threshold
\(\tau\):

\[
RUL_{i,k}=\min\{h>0: SOH_{i,k+h}\leq\tau\}.
\]

## 5. Why persistence is mandatory

The persistence forecast is

\[
\widehat{SOH}_{k+h}=SOH_k.
\]

Slowly changing degradation data can make this naive model surprisingly strong. A complex neural
network that does not beat persistence on unseen cells has not learned useful prognostic structure.

## 6. Feature mathematics

For a constant-voltage transient, steady current is estimated robustly from the final fraction of
the experiment:

\[
j_{ss}=\operatorname{median}\{j(t):t\text{ lies in the final 10\%}\}.
\]

The 90% response time is the first time at which the signed change reaches
\(j_0+0.9(j_{ss}-j_0)\). The relaxation area

\[
A_r=\int |j(t)-j_{ss}|\,dt
\]

captures both the magnitude and duration of transient polarization.

On an IV curve, power density is \(p=V|j|\), and an area-specific-resistance proxy in a chosen
quasi-linear region is

\[
ASR_{proxy}=-\frac{dV}{d|j|}.
\]

For EIS, \(Z(\omega)=Z'(\omega)+iZ''(\omega)\). The circuit-agnostic extractor reports a
high-frequency ohmic proxy, a low-minus-high-frequency polarization proxy, the frequency of the
largest capacitive arc, and the fraction of inductive points. These are descriptors—not proof that
a specific equivalent circuit is physically identified.

## 7. Error metrics and skill

For forecast errors \(e_n=\hat y_n-y_n\),

\[
MAE=\frac{1}{N}\sum |e_n|,\qquad
RMSE=\sqrt{\frac{1}{N}\sum e_n^2},\qquad
Bias=\frac{1}{N}\sum e_n.
\]

MASE divides model MAE by the in-sample one-step naive error. Values below one mean the model beats
that naive scale. R² is retained for familiarity but is not the decision metric for extrapolative
forecasting, because it can be negative and is sensitive to the variance of each test cell.

## 8. Split-conformal uncertainty

Given calibration residual scores \(s_i=|y_i-\hat y_i|\), choose the finite-sample corrected
\((1-\alpha)\) empirical quantile \(q\). A new point prediction becomes

\[
[\hat y-q,\ \hat y+q].
\]

Exchangeability is imperfect in degradation data, so coverage must be measured by cell, regime,
and horizon. The method supplies an empirical uncertainty check, not a guarantee under arbitrary
domain shift.

## 9. Right censoring

If a cell never sustains the SOH threshold crossing for three consecutive assessments, its exact
RUL is unknown; it is right-censored. The persistence rule reduces false events caused by a single
noisy dip. Replacing an unknown RUL with zero or the last observed assessment biases a model toward
shorter life. The project therefore stores a censoring flag and excludes censored exact-RUL labels
from ordinary regression unless a survival model is used.

## Interview check

**Question:** Why is a random 80/20 split invalid here?
**Answer:** Rows from the same curve, cycle, and cell are autocorrelated and share cell-specific
characteristics. Random splitting leaks those characteristics into the test set and measures
interpolation between familiar states rather than forecasting or unseen-cell generalization.
