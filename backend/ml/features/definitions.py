"""
Standard HR Feature Definitions — Declarative registry of features for predictive models.
"""

from __future__ import annotations

from backend.ml.domain.enums import FeatureDataType, FeatureSensitivity
from backend.ml.domain.models import FeatureDefinition

STANDARD_HR_FEATURES: list[FeatureDefinition] = [
    FeatureDefinition(
        name="employee_tenure_months",
        description="Total tenure in months since employee joining date",
        datatype=FeatureDataType.NUMERIC,
        source_table="employees",
        transformation_logic="months_between(current_date, joining_date)",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="hr-analytics",
        min_value=0.0,
        max_value=600.0,
    ),
    FeatureDefinition(
        name="leave_frequency_90d",
        description="Number of leave requests taken in the last 90 days",
        datatype=FeatureDataType.NUMERIC,
        source_table="leaves",
        transformation_logic="count(leaves in last 90 days)",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="hr-analytics",
        min_value=0.0,
        max_value=90.0,
    ),
    FeatureDefinition(
        name="attendance_rate_30d",
        description="Percentage of expected days attended in last 30 days (0.0 - 1.0)",
        datatype=FeatureDataType.NUMERIC,
        source_table="attendance",
        transformation_logic="present_days / expected_working_days",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="hr-analytics",
        min_value=0.0,
        max_value=1.0,
    ),
    FeatureDefinition(
        name="performance_trend_score",
        description="Normalized performance score trend over last 3 review cycles (1.0 - 5.0)",
        datatype=FeatureDataType.NUMERIC,
        source_table="performance_reviews",
        transformation_logic="weighted_average(review_scores)",
        sensitivity=FeatureSensitivity.SENSITIVE,
        owner="talent-management",
        min_value=1.0,
        max_value=5.0,
    ),
    FeatureDefinition(
        name="salary_growth_ratio_2y",
        description="Ratio of salary increase over last 24 months",
        datatype=FeatureDataType.NUMERIC,
        source_table="compensation",
        transformation_logic="(current_salary - salary_2y_ago) / salary_2y_ago",
        sensitivity=FeatureSensitivity.SENSITIVE,
        owner="comp-benefits",
        min_value=0.0,
        max_value=10.0,
    ),
    FeatureDefinition(
        name="engagement_score",
        description="Latest pulse survey engagement index (0.0 - 100.0)",
        datatype=FeatureDataType.NUMERIC,
        source_table="surveys",
        transformation_logic="normalized_survey_index",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="people-ops",
        min_value=0.0,
        max_value=100.0,
    ),
    FeatureDefinition(
        name="promotion_count",
        description="Total number of promotions received during tenure",
        datatype=FeatureDataType.NUMERIC,
        source_table="employee_promotions",
        transformation_logic="count(promotions)",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="people-ops",
        min_value=0.0,
        max_value=20.0,
    ),
]
