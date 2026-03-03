# Diabetes Prediction Model Report

<p align="right">Author: Kim Taekwon      </p>

## 1. One-Line Summary

- Our team built an AI model that predicts "diabetes risk" using health checkup data.
- We confirmed practical performance using only the core features (`sex`, `age`, `HE_BMI`, `HE_wc`, `HE_glu`).
- Additional optional features (F1-F2) were conditionally applied to the app/server after separate simulation validation, and in production we suppress false positives (FP) by applying a blended decision threshold (`BLEND_THRESHOLD=0.54`).

---

## 2. Problem We Solved

| Question | Answer |
|---|---|
| What to predict? | Diabetes vs. non-diabetes (binary classification) |
| Data source? | KNHANES 2019 (`HN19_ALL.sav`) |
| Target age | Age 19 or older |
| Ground-truth label | Diabetes/non-diabetes split based on `HE_DM_HbA1c` |

### Original Data Source

| Item | Details |
|---|---|
| Dataset name | Korea National Health and Nutrition Examination Survey (KNHANES), 8th cycle (2019-2021), 2019 raw data |
| Source file | `HN19_ALL.sav` |
| Source organization | Korea Disease Control and Prevention Agency (KDCA), KNHANES |
| Storage path in this project | `fastapi/resources/data/HN19_ALL.sav` |
| Reference document | `국민건강영양조사+제8기(2019-2021)+원시자료+이용지침서.pdf` |

### Why We Used This Data

| Reason | Description |
|---|---|
| High-trust national data | National-scale health survey data with strong quality/reliability |
| Includes diabetes-related variables | Includes key variables such as age, BMI, waist circumference, and glucose |
| Suitable for Korean population prediction | Based on Korean samples, so it is better aligned with a domestic user app |
| Documented variable system | An official codebook exists, making variable interpretation and reproducibility easier |

### Ground-Truth (Target) Construction

| Original Value | Mapped Value |
|---|---|
| 1, 2 | 0 (non-diabetes) |
| 3 | 1 (diabetes) |

---

## 3. Which Input Values (Features) Were Used?

### 3-1. Base Inputs

| Column (Korean) | Description | Value Collected in App |
|---|---|---|
| `sex(성별)` | Sex | Sex |
| `age(나이)` | Age | Age |
| `HE_BMI(BMI)` | Obesity index (BMI) | BMI |
| `HE_wc(허리둘레)` | Abdominal obesity indicator | Waist circumference |
| `HE_glu(공복 혈당)` | Fasting glucose | Glucose (optional) |

### 3-2. Additional Derived Features

| Column (Korean) | How It Is Created | Why It Was Created |
|---|---|---|
| `HE_whr(허리-신장 비율)` | `HE_wc(허리둘레)` / `HE_ht(키)` | Better reflects body-shape characteristics |
| `HE_bmi_wc(BMI×허리 보정)` | `HE_BMI(BMI)` × (`HE_wc(허리둘레)` / 100) | Captures composite information beyond a single indicator |

### 3-3. Two Experiments

| Experiment | Number of Included Features | Characteristic |
|---|---:|---|
| With glucose | 7 | Includes `HE_glu(공복 혈당)` |
| Without glucose | 6 | Predicts without `HE_glu(공복 혈당)` |

### 3-4. Stepwise Data Size vs. Original (`HN19_ALL.sav`)

| Step | Condition | Row Count (n) | Retention (vs. original) |
|---|---|---:|---:|
| Original | All records | 8,110 | 100.0% |
| 1st filter | `age(나이) >= 19` | 6,606 | 81.5% |
| 2nd filter | `HE_DM_HbA1c(당뇨 유병)` ∈ {1,2,3} | 5,914 | 72.9% |
| 3rd filter | Base feature validity (`HE_BMI(BMI)`, `HE_wc(허리둘레)`, `HE_ht(키)` > 0) | 5,874 | 72.4% |

### 3-5. Model Input DataFrame Info (Missing Status of Core/Extended Variables)

> Reference DataFrame: after 3rd filter, `n=5,874`

| Variable | non-null | Missing Rate |
|---|---:|---:|
| `sex(성별)` | 5,874 | 0.00% |
| `age(나이)` | 5,874 | 0.00% |
| `HE_BMI(BMI)` | 5,874 | 0.00% |
| `HE_wc(허리둘레)` | 5,874 | 0.00% |
| `HE_ht(키)` | 5,874 | 0.00% |
| `HE_glu(공복 혈당)` | 5,874 | 0.00% |
| `F1_family_dm(가족력)` | 5,292 | 9.91% |
| `F2_htn_or_med(고혈압/혈압약)` | 5,864 | 0.17% |

> Note: `HE_glu(공복 혈당)` has some high-value outliers in the full dataset, and the app API uses an input range of 44-199.  
> Among 5,874 base valid samples, 5,813 records fall within the app input range (44-199).

### 3-6. Summary Statistics of Core Continuous Variables (Describe, base valid sample n=5,874)

| Variable | mean | std | min | 25% | 50%(median) | 75% | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| `age(나이)` | 51.57 | 16.78 | 19.0 | 38.0 | 52.0 | 65.0 | 80.0 |
| `HE_BMI(BMI)` | 23.92 | 3.59 | 13.98 | 21.47 | 23.60 | 25.99 | 50.29 |
| `HE_wc(허리둘레)` | 83.97 | 10.41 | 53.0 | 76.6 | 83.8 | 90.8 | 135.9 |
| `HE_ht(키)` | 163.69 | 9.36 | 133.3 | 156.7 | 163.3 | 170.5 | 194.0 |
| `HE_glu(공복 혈당)` | 101.23 | 22.42 | 53.0 | 90.0 | 96.0 | 105.0 | 339.0 |

### 3-7. Core Features vs. Extended Candidate Features (From pre-validation/conditional-application perspective)

| Category | Variable (Korean) | Initial Model (Core Features) | Extended Candidate Validation | Data Quality/Observation |
|---|---|---|---|---|
| Core (base) | `sex(성별)`, `age(나이)`, `HE_BMI(BMI)`, `HE_wc(허리둘레)`, `HE_glu(공복 혈당)` | Used | Kept as baseline features | Low missingness and stable |
| Extension F1 | `HE_DMfh1/2/3(가족 당뇨 진단력)` | Conditionally used (no-glucose path) | Pre-validation + conditional application completed | ~9.9% missing; auxiliary feature value confirmed in no_glu path |
| Extension F2 | `DI1_dg`, `HE_HPdr`, `HE_HP`(고혈압/혈압약) | Conditionally used (priority application) | Pre-validation + conditional application completed | Very low missingness; improvements dominant in binned/exact paths |

### 3-8. Data Status Visualization Charts

- ![Data Funnel](../simulation/fig_data_funnel.png)
- ![Feature Coverage](../simulation/fig_feature_coverage.png)
- ![Core Feature Boxplot](../simulation/fig_core_feature_boxplot.png)

| Chart | Key Message |
|---|---|
| Data Funnel | Shows convergence from 8,110 original rows to 5,874 model-valid rows |
| Feature Coverage | Shows coverage distribution of core variables and F1/F2 |
| Core Feature Boxplot | Provides intuitive ranges for `age(나이)`, `HE_BMI(BMI)`, `HE_wc(허리둘레)`, `HE_glu(공복 혈당)` |

---

## 4. Data Preprocessing (Data Preparation) Pipeline

"Preprocessing" is the process of preparing data so the model can learn effectively.

| Step | Action | Description |
|---|---|---|
| 1 | Keep adults only | Use age 19+ only |
| 2 | Label conversion | Simplify to diabetes/non-diabetes binary labels |
| 3 | Missing-value handling | Fill missing entries |
| 4 | Standardization | Bring values to a similar scale |
| 5 | Add derived features | Create new information such as waist-height ratio |
| 6 | SMOTE | Balance classes when diabetes samples are insufficient |

### Standardization vs. Normalization: Why Standardization?

| Method | Meaning | Choice in This Project |
|---|---|---|
| Normalization | Scales values to 0-1 | Not selected |
| Standardization | Scales to mean 0, std 1 | **Selected** |

Reason for selection: Distance-based models such as KNN were used, and standardization was more stable.

---

## 5. Train/Validation/Test Split

| Data Split | Ratio | Role |
|---|---:|---|
| Train | 70% | Model training |
| Validation | 10% | Threshold tuning |
| Test | 20% | Final performance evaluation |

In simple terms:
- **Train**: used for fitting the model
- **Validation**: used for threshold tuning
- **Test**: used for final performance evaluation

---

## 6. Which Models Were Compared, and Why Was This Model Selected?

### 6-1. Compared Models

| Category | Models |
|---|---|
| Linear | LogisticRegression, SGDClassifier |
| Tree/Ensemble | RandomForest, GradientBoosting, AdaBoost |
| Distance/Margin | KNN, SVM |
| Neural network | MLPClassifier |

### 6-2. Final Selection

In both experiments, **KNN** achieved the best score.

| Experiment | Final Model | Key Hyperparameters |
|---|---|---|
| With glucose | KNN | `n_neighbors=3`, `weights=distance`, `p=2` |
| Without glucose | KNN | `n_neighbors=3`, `weights=distance`, `p=2` |

### 6-3. Hyperparameter Selection Process

- Compared parameter combinations using Grid Search.
- Scoring criterion: `balanced_recall`  
  (reflects both overall accuracy and patient detection ability [Recall])

---

## 7. Performance Results (Numbers)

### 7-1. Key Metric Comparison

| Metric | With glucose (base+`HE_glu`) | Without glucose (base only) |
|---|---:|---:|
| Accuracy | 0.8368 | 0.6675 |
| Precision | 0.4516 | 0.2267 |
| Recall | 0.8284 | 0.6036 |
| F1 | 0.5846 | 0.3296 |
| ROC-AUC | 0.8608 | 0.6565 |

### 7-2. Why Accuracy Alone Is Not Enough

In medical problems, "not missing true patients" is critical.  
So we placed special emphasis on **Recall**.

| Metric | Meaning | Why It Matters |
|---|---|---|
| Accuracy | Overall correct prediction ratio | Reference only |
| Precision | Among predicted diabetes cases, true positive ratio | Warning precision |
| Recall | How well actual diabetes is found | Very important in medical settings |
| F1 | Balance between Precision/Recall | Overall judgment |

---

## 8. Confusion Matrix (Prediction Summary)

| Experiment | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| With glucose | 880 | 170 | 29 | 140 |
| Without glucose | 731 | 348 | 67 | 102 |

Interpretation:
- Fewer **FN (missed patients)** is better for medical use.
- The glucose-included model is safer because it has fewer FN.

---

## 9. Which Model Is Better for Medical Use?

Conclusion: The **KNN model with glucose** is more suitable.

Reasons:
1. Higher Recall (finds patients better)
2. Higher ROC-AUC (better overall discrimination)
3. Fewer FN in the confusion matrix (fewer missed patients)

---

## 10. Do We Need All Columns in the App Implementation?

Conclusion: **No. Only core inputs are required.**

| Category | Items (Variables) | Description |
|---|---|---|
| Direct app input | Sex (`sex`), age (`age`), height (`height_cm`), weight (for `HE_BMI` calculation), waist circumference (`HE_wc`) | Entered directly by user in the app |
| Optional app input | Glucose (`HE_glu`) | If provided, model with glucose is used |
| App-side calculation | BMI (`HE_BMI`) | Calculated from height/weight in app and sent to server |
| Server-side calculation | `HE_whr(허리-신장 비율)` | `HE_wc(허리둘레)` / `HE_ht(키)` |
| Server-side calculation | `HE_bmi_wc(BMI×허리 보정)` | `HE_BMI(BMI)` × (`HE_wc(허리둘레)`/100) |

> Production input policy: `HE_wc(허리둘레)` remains a **required input** in this app.

---

## 11. Results in Figures (Visualization Summary)

### Figure 1. Test Metric Comparison
![Figure 1](./assets/fig_01_test_metrics_comparison.png)

- This chart compares key performance metrics across two scenarios (with/without glucose).
- X-axis: metric type (Accuracy, Precision, Recall, F1, ROC-AUC)
- Y-axis: score (0-1)
- Interpretation point: **higher bars indicate better performance**. The with-glucose bars are higher for most metrics.

### Figure 2. Cross-Validation (CV) Score and Threshold Comparison
![Figure 2](./assets/fig_02_cv_threshold_comparison.png)

- This chart compares the CV score used for model selection and the final threshold.
- X-axis: `Best CV Score`, `Threshold`
- Y-axis: value (0-1)
- Interpretation point: higher CV score is better; threshold meaning depends on operating objective (sensitivity/precision), rather than being simply high or low.

### Figure 3. Radar Chart (Overall Performance)
![Figure 3](./assets/fig_03_metrics_radar.png)

- This chart provides an overall comparison by showing multiple metrics simultaneously in a radial plot.
- Each axis (radial axis): Accuracy, Balanced Accuracy, Precision, Recall, F1, ROC-AUC
- Scores increase from center to outer edge (0→1)
- Interpretation point: wider and more outward area indicates better overall performance. The with-glucose model covers a larger area.

### Figure 4. Confusion Matrix Comparison
![Figure 4](./assets/fig_04_confusion_matrix_comparison.png)

- This chart shows correct/incorrect predictions in a 2x2 table.
- X-axis: model predictions (Pred 0, Pred 1), Y-axis: true labels (True 0, True 1)
- Cell meaning: TN (correct normal), FP (normal predicted as diabetes), FN (diabetes missed as normal), TP (correct diabetes)
- Interpretation point: from a medical perspective, **lower FN is better**. The with-glucose model has lower FN.

### Figure 5. ROC Curve Comparison
![Figure 5](./assets/fig_05_roc_curve_comparison.png)

- This chart shows how discriminative performance changes as threshold changes.
- X-axis: FPR (False Positive Rate)
- Y-axis: TPR (True Positive Rate = Recall)
- Interpretation point: curves closer to the **top-left** are better, and higher AUC is better.

### Figure 6. Number of Input Features Comparison
![Figure 6](./assets/fig_06_feature_count.png)

- This chart compares input feature counts by scenario.
- X-axis: number of features
- Y-axis: scenario (with/without glucose)
- Interpretation point: the with-glucose scenario has one additional feature (`HE_glu`).

### Figure 7. Precision/Recall/F1 Comparison
![Figure 7](./assets/fig_07_positive_class_metrics.png)

- This chart compares only positive-class (diabetes) metrics.
- X-axis: Precision, Recall, F1
- Y-axis: score (0-1)
- Interpretation point: **higher bars are better**. The Recall difference especially highlights patient-detection capability.

### Figure 8. Error Type (FP/FN) Comparison
![Figure 8](./assets/fig_08_error_type_comparison.png)

- This chart compares counts of two key model errors (FP, FN).
- X-axis: error type (FP, FN)
- Y-axis: number of errors (count)
- Interpretation point: in medical screening, reducing FN (missed patients) is important. **Lower bars are preferred**.

---

## 12. Reproducibility (Run Again)

```bash
cd fastapi
source .venv/bin/activate

# Train model with glucose
python train_knhanes.py --with-glucose --feature-eng --poly --smote --score-by balanced_recall --save

# Train model without glucose
python train_knhanes.py --feature-eng --poly --smote --score-by balanced_recall --save
```

Data file location:
- `fastapi/resources/data/HN19_ALL.sav`

---

## 13. Production Scenario Simulation (Current App Logic)

### 13-1. Terminology

| Term | Definition |
|---|---|
| `glu_exact` | `HE_glu(공복 혈당)` entered as a continuous value (exact value) |
| `glu_binned` | Glucose entered by range (midpoint) |
| `no_glu` | `HE_glu(공복 혈당)` not entered |
| `blend` | Probability blending to reduce glucose dependency: `0.55 * no_glu + 0.45 * glu` |
| `blend_exact` | Glucose + other risk-factor blend (exact glucose input) |
| `blend_binned` | Glucose + other risk-factor blend (binned glucose input) |

### 13-2. Simulation Result Table (`resources/simulation/simulation_summary.csv`)

> Note: In this table, **prediction rate** means `Accuracy`.  
> Note: `FN` is count of missed diabetes cases, and `FP` is count of non-diabetes predicted as diabetes.

| Scenario | Accuracy | Precision | Recall | F1 | ROC-AUC | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| glu_exact | 0.9475 | 0.7526 | 0.9108 | 0.8242 | 0.9444 | 47 | 14 |
| glu_binned | 0.8590 | 0.4877 | 0.8854 | 0.6290 | 0.9116 | 146 | 18 |
| no_glu | 0.9020 | 0.5923 | 0.8790 | 0.7077 | 0.9156 | 95 | 19 |
| blend_exact | 0.8942 | 0.5620 | 0.9809 | 0.7146 | 0.9840 | 120 | 3 |
| blend_binned | 0.8564 | 0.4843 | 0.9809 | 0.6484 | 0.9783 | 164 | 3 |

> One-line takeaway: **Highest Accuracy** is `glu_exact (94.75%)`,  
> **Highest Recall** is `blend_exact/blend_binned (98.09%)`.

### 13-3. Interpretation Summary

| Perspective | Interpretation |
|---|---|
| Best overall performance | `glu_exact` is best in Accuracy and F1 |
| Glucose range input | `glu_binned` has information loss compared to exact input |
| FN-minimizing operation | `blend` is favorable for reducing FN, with an FP increase tradeoff |

### 13-4. Charts

- ![Simulation Metrics](../simulation/fig_simulation_metrics.png)
- ![Simulation Errors](../simulation/fig_simulation_errors.png)

### 13-5. Blend Operating Point (Threshold) Tuning Results

> The values below were obtained by tuning only the final classification threshold on blend probabilities, without retraining.  
> Applied setting: fixed `GLUCOSE_BLEND_WEIGHT=0.55`, increased `BLEND_THRESHOLD`.

| Category | weight | threshold | exact (FP/FN) | binned (FP/FN) |
|---|---:|---:|---:|---:|
| Before tuning (detection-maximizing operating point) | 0.55 | 0.15 | 120 / 3 | 164 / 3 |
| After tuning (FP-suppressing operating point) | 0.55 | 0.54 | 32 / 21 | 45 / 20 |

- Interpretation:
  - Increasing threshold greatly reduces false positives (FP).
  - FN (misses) increases in return, so operating point selection should follow objective (FP suppression vs. miss minimization).
- Output files:
  - `resources/simulation/blend_threshold_sweep.csv`
  - `resources/simulation/blend_threshold_tuning.md`

---

## 14. F1-F2 Pre-Validation Results (Additional Feature Plan)

### 14-1. Planned Feature Mapping Table

| Planned Feature | Data Variable (Korean) | Application Status |
|---|---|---|
| F1 Family history | `HE_DMfh1(부 당뇨 진단력)`, `HE_DMfh2(모 당뇨 진단력)`, `HE_DMfh3(형제자매 당뇨 진단력)` | Simulation mapping completed |
| F2 Hypertension/medication | `DI1_dg(고혈압 의사진단)`, `HE_HPdr(검진당일 혈압약 복용)`, `HE_HP(고혈압 유병)` | Simulation mapping completed |

### 14-2. Result Table Including F1/F2 Ablation (`resources/simulation/feature_plan_simulation_summary.csv`)

> Terminology: in `optional mode`, `none` = no optional inputs, `f1` = family history only, `f2` = hypertension/medication only, `f12` = both  
> Terminology: in `glucose mode`, `none` = no glucose, `binned` = binned glucose, `exact` = exact glucose

| Scenario | Optional mode | Glucose mode | Accuracy | Precision | Recall | F1 | ROC-AUC | FP | FN |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| base_no_glu | none | none | 0.7219 | 0.2830 | 0.6095 | 0.3865 | 0.6974 | 261 | 66 |
| opt1_no_glu | f1 | none | 0.7287 | 0.2984 | 0.6568 | 0.4104 | 0.7211 | 261 | 58 |
| opt2_no_glu | f2 | none | 0.7134 | 0.2801 | 0.6331 | 0.3884 | 0.6955 | 275 | 62 |
| opt12_no_glu | f12 | none | 0.7245 | 0.2817 | 0.5917 | 0.3817 | 0.6852 | 255 | 69 |
| base_glu_binned | none | binned | 0.8673 | 0.5243 | 0.8284 | 0.6422 | 0.8892 | 127 | 29 |
| opt1_glu_binned | f1 | binned | 0.8690 | 0.5283 | 0.8284 | 0.6452 | 0.8875 | 125 | 29 |
| opt2_glu_binned | f2 | binned | 0.8741 | 0.5399 | 0.8402 | 0.6574 | 0.8901 | 121 | 27 |
| opt12_glu_binned | f12 | binned | 0.8648 | 0.5182 | 0.8402 | 0.6411 | 0.8873 | 132 | 27 |
| base_glu_exact | none | exact | 0.8818 | 0.5586 | 0.8462 | 0.6729 | 0.8995 | 113 | 26 |
| opt1_glu_exact | f1 | exact | 0.8801 | 0.5551 | 0.8343 | 0.6667 | 0.8983 | 113 | 28 |
| opt2_glu_exact | f2 | exact | 0.8920 | 0.5868 | 0.8402 | 0.6910 | 0.9042 | 100 | 27 |
| opt12_glu_exact | f12 | exact | 0.8665 | 0.5219 | 0.8462 | 0.6456 | 0.8965 | 131 | 26 |

### 14-3. Interpretation Summary

| Segment | Interpretation |
|---|---|
| No glucose (`none`) | `F1` alone improves Recall (+0.0473) and FN (-8). `F2` slightly improves Recall but increases FP. Simultaneous `F1+F2` is not recommended due to worse Recall/FN |
| Binned glucose (`binned`) | `F2` alone improves Accuracy/Precision/Recall/F1 (dominant). `F1+F2` improves Recall only, while Accuracy/Precision decrease |
| Exact glucose (`exact`) | `F2` alone improves Accuracy/Precision/F1, while Recall slightly drops (-0.0060). Benefit of `F1` alone or `F1+F2` is limited |

### 14-4. Charts

- ![Feature Plan Metrics](../simulation/feature_plan_sim_metrics.png)
- ![Feature Plan Errors](../simulation/feature_plan_sim_errors.png)

---

## 15. Application Review Outcome and Future Plan

| Item | Review Criteria | Summary in This Report |
|---|---|---|
| Simple tab | Minimize input burden | Keep current design (no change) |
| Detailed tab | Performance gain + user acceptability | Conditional extension under review (centered on F1, F2) |
| F1 family history | Recall/FN improvement confirmed in no_glu segment, limited benefit when glucose is entered | Conditional candidate (priority in no-glucose path) |
| F2 hypertension/medication | Reproduced Accuracy/F1 gains in binned/exact segments | Priority candidate for review (1st priority in detailed tab) |
| Waist circumference input | User input feasibility and model stability | Keep as required input |
| Operational monitoring | Track Recall/FN/FP | Quarterly performance checks |

---

## 16. Additional Reproduction Commands (Simulation)

```bash
cd fastapi
source .venv/bin/activate

# Production-scenario simulation (including blend)
python simulate_optional_input_cases.py

# Simulation with/without planned features (F1-F2)
python simulate_feature_plan_cases.py

# Operating-point tuning without retraining (blend weight / threshold)
python tune_blend_operating_point.py
```

---

## 17. Summary and Future Deployment Direction

| Item | Summary |
|---|---|
| Product structure | Keep the simple tab, and gradually review extended items in the detailed tab |
| Input policy | Keep `HE_wc(허리둘레)` as a required input |
| Extension priority | F2 (hypertension/medication) first, then conditional review of F1 (family history) |
| Operations direction | Keep the baseline path; reflect extended paths based on validation outcomes |
| Operational parameters | Apply `GLUCOSE_BLEND_WEIGHT=0.55`, `BLEND_THRESHOLD=0.54` (for FP suppression) |

### 17-1. Stepwise Rollout Proposal (Draft)

1. **Phase 1**: Review F2-only integration in detailed-tab extended path (especially binned/exact), track Recall/FP/FN  
2. **Phase 2**: Review conditional F1 integration focused on no-glucose path and re-evaluate

### 17-2. Performance Review Criteria

| Category | Criteria (Review Metrics) |
|---|---|
| Improvement judgment | After detailed-tab extension, confirm improved `Recall` or reduced `FN` |
| Warning signal | Repeated performance drop in exact-glucose segment or sudden FP increase |

---

## 18. API Dummy Test Cases (Live Responses)

To verify server policies (F2 priority, F1 conditional, automatic exclusion outside KNHANES), we made real `/predict` calls.

- Run date/time: 2026-02-21
- Runtime environment: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Common: `chart_image_base64` in responses is omitted in the table

### 18-1. Case Summary Table

| Case | Purpose | HTTP | Prediction result (prediction/probability) | Used model (`used_model`) | Policy verification point |
|---|---|---:|---|---|---|
| case1_knhanes_no_glu_f1f2 | No glucose + F1/F2 both entered | 200 | 1 / 1.0 | KNHANES without glucose | `input` includes both `family_history_dm` and `htn_or_med` |
| case2_knhanes_glu_f1f2 | Glucose entered + F1/F2 both entered | 200 | 1 / 0.55 | KNHANES blend | `family_history_dm` excluded from `input`, `htn_or_med` retained |
| case3_knhanes_glu_f2_only | Glucose entered + F2 only | 200 | 1 / 0.1607 | KNHANES blend | `input` includes only `htn_or_med` |
| case4_pima_with_f1f2 | Pima path + F1/F2 entered | 200 | 0 / 0.4062 | AdaBoost (with glucose) | F1/F2 automatically excluded from `input` |
| case5_range_error | Range error (glucose 300) | 400 | - | - | Verify range-validation error message |
| case6_minimal_no_glu | Minimal input (no glucose) | 200 | 1 / 1.0 | KNHANES without glucose | Verify normal response in baseline path |

### 18-2. Key Live Response Excerpts (JSON)

#### case2_knhanes_glu_f1f2 (Glucose entered + F1/F2 both entered)

```json
{
  "prediction": 1,
  "probability": 0.55,
  "used_model": "KNHANES blend (55% risk factors + 45% glucose)",
  "input": {
    "glucose": 95.0,
    "bmi": 28.0,
    "age": 47.0,
    "waist_cm": 94.0,
    "sex": 1.0,
    "height_cm": 170.0,
    "htn_or_med": 0.0
  }
}
```

Verification: Although `family history` was included in the request, it was excluded from response `input`, confirming server policy application.

#### case4_pima_with_f1f2 (Pima path + F1/F2 entered)

```json
{
  "prediction": 0,
  "probability": 0.4062,
  "used_model": "AdaBoost (with glucose)",
  "input": {
    "pregnancies": 2.0,
    "glucose": 95.0,
    "bmi": 28.0,
    "age": 47.0
  }
}
```

Verification: In the Pima path, `family_history_dm` and `htn_or_med` are automatically excluded.

#### case5_range_error (Glucose range error)

```json
{
  "detail": "glucose must be within the range 44.0 to 199.0."
}
```

Verification: Input range validation works as expected.
