
@startuml UsecaseAI
left to right direction
skinparam packageStyle rectangle

actor "Nutritionist" as N
actor "Doctor" as D
actor "Finance Staff" as F
actor "Admin Staff" as A

rectangle "AI Assistant System" {

  package "Nutritionist Use Cases" {
    usecase "Calculate Calorie Needs\n(Aoikumo: GET /patients/{id}/profile)" as UC1
    usecase "Generate Diabetic Meal Plan\n(Aoikumo: GET /patients/{id}/diet-log)" as UC2
    usecase "Retrieve Allergy Info\n(Aoikumo: GET /patients/{id}/allergies)" as UC3
    usecase "Protein Intake for CKD\n(Aoikumo: GET /patients/{id}/lab-results)" as UC4
    usecase "Nutrient Summary Report\n(Aoikumo: GET /patients/{id}/diet-log)" as UC5
    usecase "Detect Nutrient Deficiency Trends\n(No API—needs Aoikumo data only)" as UC6
    usecase "Predict Nutrition Risk\n(No API—needs Aoikumo data only)" as UC7
  }

  package "Doctor Use Cases" {
    usecase "Summarize Visit History\n(Aoikumo: GET /patients/{id}/visits)" as UC8
    usecase "Symptom Cause Analyzer\n(No API—needs Aoikumo data only)" as UC10
    usecase "Auto‑Generate Discharge Summary\n(Aoikumo: GET /patients/{id}/visits)" as UC11
    usecase "Treatment Plan Suggestion\n(No API—needs Aoikumo data only)" as UC12
  }

  package "Finance Use Cases" {
    usecase "View Outstanding Balance\n(AutoCount: GET /receivables; Aoikumo: GET /patients/{id}/billing)" as UC15
    usecase "Monthly Revenue Report\n(AutoCount: GET /revenue/summary)" as UC16
    usecase "Billing Discrepancy Detection\n(AutoCount + Aoikumo)" as UC17
    usecase "Profitability Analysis\n(AutoCount + AI)" as UC19
    usecase "Detect Financial Anomalies\n(AutoCount + AI)" as UC20
  }

  package "Admin Use Cases" {
    usecase "Appointment Count Summary\n(Aoikumo: GET /appointments?date=…)" as UC21
    usecase "Auto Send Appointment Reminders\n(Aoikumo: GET /appointments + POST /messages)" as UC22
    usecase "Identify Inactive Patients\n(No API—needs Aoikumo data only)" as UC23
    usecase "Daily Operations Report\n(Aoikumo + AutoCount + Pipedrive: GET /activities)" as UC24
    usecase "Doctor Availability Checker\n(Aoikumo: GET /schedules/{doctorId})" as UC25
    usecase "No‑Show Risk Predictor\n(No API—needs Aoikumo data only)" as UC26
  }
}

N --> UC1
N --> UC2
N --> UC3
N --> UC4
N --> UC5
N --> UC6
N --> UC7

D --> UC8
D --> UC10
D --> UC11
D --> UC12


F --> UC15
F --> UC16
F --> UC17
F --> UC19
F --> UC20

A --> UC21
A --> UC22
A --> UC23
A --> UC24
A --> UC25
A --> UC26
@enduml

