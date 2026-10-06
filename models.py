from typing import Literal
from pydantic import BaseModel, Field


class KeyMertic(BaseModel):
    name: str = Field(description="اسم المؤشر التشغيلي")
    value: str = Field(description="قيمة المؤشر")
    meaning: str = Field(description= "ماذا تعني هذه القيمة إداريا")


class OperationalInsight(BaseModel):
    title: str = Field(description="عنوان التنبيه التشغيلي")
    severity: Literal["low","medium","high"] = Field(description="درجة أهمية التنبيه")
    evidence: str = Field(description="الدليل من البيانات")
    possible_cause: str = Field(description="السبب المحتمل للمشكلة")
    recommended_action: str = Field(deprecated="الإجراء المقترح")


class PropsedAction(BaseModel):
    action_type: Literal[
              "follow_up",
              "message_draft",
              "branch_review",
              "shipment_check",
              "no_action"               
                         
                         
    ]
    description: str = Field(description="وصف الإجراء المقترح")
    requires_human_approval: bool =  Field(description="هل يحتاج الإجراء موافقة بشرية؟")


class DraftMessage(BaseModel):
    target: str = Field(description="الجهة المستهدفة بالرسالة")
    reason: str = Field(description="سبب الرسالة أو المتابعة")
    message: str = Field(description="نص الرسالة المقترحة")
    requires_human_approval: bool  = Field(description="هل تحتاج الرسالة إلى مراجعة بشرية قبل الإرسال؟")



class OperationAnswer(BaseModel):
    answer: str = Field(description="الإجابة النهائية المختصرة للمستخدم")
    used_data_sources: list[str] = Field(description="مصادر البيانات أو مسارات API التي اعتمد عليها الوكيل")
    key_metrics: list[KeyMertic] = Field(description="أهم المؤشرات التشغيلية المستخرجة من البيانات")
    operational_insights: list[OperationalInsight] = Field(description="تنبيهات تشغيلية ذكية مستنتجة من البيانات")
    proposed_actions: list[PropsedAction] = Field(description="إجراءات مقترحة آمنة للمراجعة البشرية")
    draft_messages: list[DraftMessage] = Field(default_factory=list, description="مسودات رسائل جاهزة للمراجعة البشرية قبل الإرسال" )
