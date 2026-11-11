"""
Pydantic schemas for MFG006 Disruption Machine Learning endpoints.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MFG006PredictRequest(BaseModel):
    """
    Validated pre-disruption feature input schema.
    Only pre-disruption features are accepted to prevent target leakage.
    """
    model_config = ConfigDict(extra="ignore")

    # Supplier Profile (Numerical)
    supplier_tier: int = Field(default=1, ge=1, le=4, description="Supplier tier level (1 to 4)")
    supplier_geographic_risk_score: float = Field(default=5.0, ge=0.0, le=10.0, description="Geographic risk score (0-10)")
    number_of_alternative_suppliers: int = Field(default=1, ge=0, description="Count of qualified alternative suppliers")
    supplier_concentration_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Procurement volume concentration (%)")
    affected_sku_count: int = Field(default=10, ge=0, description="Number of SKUs dependent on component")
    supplier_financial_health_score: float = Field(default=6.0, ge=0.0, le=10.0, description="Financial health rating (0-10)")
    supplier_audit_score_last: float = Field(default=70.0, ge=0.0, le=100.0, description="Most recent audit score (0-100)")
    months_since_last_audit: int = Field(default=12, ge=0, description="Months elapsed since last audit")
    supplier_relationship_years: float = Field(default=5.0, ge=0.0, description="Tenure of relationship in years")
    supply_volume_at_risk_units: int = Field(default=50000, ge=0, description="Expected cycle delivery volume exposed")
    revenue_at_risk_usd: float = Field(default=1000000.0, ge=0.0, description="Revenue exposed to this component (USD)")
    inventory_buffer_days_at_onset: float = Field(default=25.0, ge=0.0, description="Days of on-hand inventory buffer")
    normal_lead_time_days: float = Field(default=45.0, ge=1.0, description="Contracted nominal lead time in days")
    freight_cost_normal_usd: float = Field(default=15000.0, ge=0.0, description="Baseline shipping cost (USD)")
    demand_volatility_index: float = Field(default=20.0, ge=0.0, description="Historical demand volatility index")
    demand_forecast_error_mape: float = Field(default=30.0, ge=0.0, description="Demand forecast error MAPE (%)")
    order_variability_bullwhip_ratio: float = Field(default=2.0, ge=0.0, description="Order variability bullwhip ratio")
    customer_concentration_top3_pct: float = Field(default=40.0, ge=0.0, le=100.0, description="Top 3 customers demand share (%)")
    early_warning_lead_days: int = Field(default=0, ge=0, description="Days of advance warning notice")
    supply_chain_visibility_score: float = Field(default=3.0, ge=0.0, le=5.0, description="End-to-end digital visibility (0-5)")
    supply_chain_maturity_score: float = Field(default=3.0, ge=0.0, le=5.0, description="Supply chain maturity rating (0-5)")

    # Supplier Profile (Categorical)
    industry_sector: str = Field(default="electronics", description="Industry sector (e.g. electronics, automotive)")
    disruption_category: str = Field(default="supplier_failure", description="Threat category being assessed")
    disruption_subcategory: str = Field(default="quality_failure", description="Specific threat scenario type")
    affected_region: str = Field(default="Western_Europe", description="Geographic supply chain macro-region")
    supplier_criticality: str = Field(default="preferred", description="Contractual classification (preferred, sole_source, etc.)")
    supplier_country: str = Field(default="US", description="Supplier facility country ISO code")
    affected_component_category: str = Field(default="electronic_component", description="Component category")
    logistics_mode_primary: str = Field(default="ocean_freight", description="Primary transport mode")
    logistics_concentration_risk: str = Field(default="dual_carrier", description="Carrier concentration profile")
    safety_stock_adequacy: str = Field(default="adequate", description="Safety stock status (adequate, marginal, insufficient, critical)")
    early_warning_source: str = Field(default="none", description="Source of advance warning")
    resilience_posture_pre_event: str = Field(default="compliant", description="Pre-event preparedness posture")

    # Supplier Profile (Boolean)
    dual_source_in_place: bool = Field(default=True, description="Whether dual sourcing agreement exists")
    nearshoring_available: bool = Field(default=False, description="Whether nearshoring alternative is available")
    early_warning_signal_detected: bool = Field(default=False, description="Whether advance warning was flagged")
    digital_twin_available: bool = Field(default=False, description="Whether supply chain digital twin exists")
    erp_alert_triggered: bool = Field(default=False, description="Whether automated ERP alert triggered")
    external_data_feed_active: bool = Field(default=False, description="Whether external risk feeds are active")
    tier2_visibility_flag: bool = Field(default=False, description="Whether Tier-2 visibility exists")

    model_name: Optional[str] = Field(default="XGBoost", description="Model to use: 'XGBoost' (recommended) or 'Random Forest'")


class MFG006PredictResponse(BaseModel):
    predicted_risk: str = Field(..., description="Predicted severity level ('low', 'medium', 'high', 'critical')")
    probabilities: Dict[str, float] = Field(..., description="Softmax class probability distribution")
    expected_severity_index: float = Field(..., description="Continuous severity gradient index (1.0 to 4.0)")
    model: str = Field(..., description="Model identifier used for inference")
    model_version: str = Field(default="1.0.0", description="Model artifact version")


class ContributingFeature(BaseModel):
    feature: str
    clean_name: str
    value: Any
    importance_rank: int
    global_importance_score: float
    direction: str  # "Risk Driver" or "Resilience Buffer"


class MFG006ExplanationResponse(BaseModel):
    predicted_risk: str
    probabilities: Dict[str, float]
    model: str
    important_contributing_features: List[ContributingFeature]
    explanation: List[str]
    limitation: str = Field(
        default="Feature importance identifies statistical tree-split associations in training data; it does not constitute deterministic physical causation.",
        description="Scientific explainability disclaimer"
    )


class MLHealthResponse(BaseModel):
    status: str
    preprocessor_loaded: bool
    models_available: List[str]
    total_pre_disruption_features: int
    target_classes: List[str]
    library_versions: Dict[str, str]
