# 요청/응답 스키마 (한글 alias 지원)
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    """예측 입력 (한글 키 가능)"""
    pregnancies: float | None = Field(None, alias="임신횟수")
    glucose: float | None = Field(None, alias="혈당")
    bmi: float | None = Field(None, alias="BMI")
    age: float | None = Field(None, alias="나이")
    waist_cm: float | None = Field(None, alias="허리둘레")
    sex: int | None = Field(None, alias="성별")  # 1=남, 2=여 (KNHANES)
    height_cm: float | None = Field(None, alias="키")  # HE_whr 계산용
    family_history_dm: int | None = Field(None, alias="가족력")  # 0=없음, 1=있음
    htn_or_med: int | None = Field(None, alias="고혈압/혈압약")  # 0=아니오, 1=예

    model_config = ConfigDict(populate_by_name=True)


class PredictResponse(BaseModel):
    """예측 결과"""
    prediction: int
    probability: float
    # 보정 전 순수 ML 확률(운영 모니터링용)
    # - 가드레일로 표시 확률(probability)을 조정해도, 모델 원본 출력은 추적 가능해야 한다.
    ml_probability: float
    # 혈당 임상 기준 가드레일이 이번 요청에서 발동했는지 여부
    # - True면 probability가 안전 보정 로직의 영향을 받았을 가능성이 있다.
    guardrail_applied: bool
    label: str
    input: dict[str, float]
    used_model: str
    chart_image_base64: str | None = None


class GeocodeRequest(BaseModel):
    """주소 입력"""
    address: str = Field(..., description="변환할 주소")


class GeocodeResponse(BaseModel):
    """lat/lng 반환"""
    lat: str
    lng: str
