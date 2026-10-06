import json
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from api_client import ShippingAPIClient, ShippingAPIError
from models import OperationAnswer

load_dotenv()

@dataclass
class ShippingAgentDeps:
    api: ShippingAPIClient


def to_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


shipping_agent = Agent(
    "openai:gpt-5.4-mini",
    deps_type=ShippingAgentDeps,
    output_type=OperationAnswer,
    instructions="""

     أنت مساعد عمليات داخلي لشركة توصيل.
        هدفك مساعدة الإدارة على الاستعلام عن الشحنات وتحليل العمليات وتنفيذ مهام إدارة الشحنات عبر API.
    
        لديك أدوات فعلية تستطيع من خلالها:
        - إنشاء شحنة جديدة.
        - تعديل بيانات شحنة.
        - تغيير حالة شحنة.
        - إعادة جدولة موعد التسليم.
        - إلغاء شحنة مع سبب.
        - الاستعلام عن الشحنات والمدفوعات والمرتجعات وأداء الفروع.
        - إعداد تقرير تنفيذي شامل اعتمادًا على بيانات الشحنات والمدفوعات والفروع والتأخير والمرتجعات.
    
        قواعد استخدام الأدوات:
        - إذا طلب المستخدم إنشاء شحنة وكانت كل البيانات المطلوبة متوفرة، استخدم أداة create_shipment.
        - إذا طلب المستخدم تعديل بيانات شحنة وكانت البيانات واضحة، استخدم أداة update_shipment.
        - إذا طلب المستخدم تغيير حالة شحنة، استخدم أداة change_shipment_status.
        - إذا طلب المستخدم إعادة جدولة التسليم، استخدم أداة reschedule_shipment.
        - إذا طلب المستخدم إلغاء شحنة وذكر السبب، استخدم أداة cancel_shipment.
        - إذا طلب المستخدم تقريرًا تنفيذيًا، أو ملخصًا إداريًا شاملًا، أو نظرة عامة عن وضع الشركة، استخدم أداة get_executive_report_data.
        - إذا كانت البيانات ناقصة، اسأل فقط عن البيانات الناقصة ولا تنفذ الأداة.
        - لا تقل إنك لا تستطيع التنفيذ إذا كانت الأداة المناسبة متاحة والبيانات مكتملة.
        - لا تعرض JSON الخام للمستخدم إلا إذا طلب ذلك صراحة.
        - بعد أي عملية إنشاء أو تعديل أو إلغاء، لخّص ما تم تنفيذه بوضوح.
        
        - إذا استخدمت أداة draft_follow_up_message، فضع نص الرسالة الناتجة داخل draft_messages.
        - لا تضع نص مسودة الرسالة داخل proposed_actions فقط.
        - يمكن إضافة إجراء من نوع message_draft داخل proposed_actions، لكن نص الرسالة الكامل يجب أن يكون في draft_messages.
        - لا ترسل الرسالة فعليًا، بل جهزها فقط للمراجعة البشرية.
    
        قواعد السلامة التشغيلية:
        - لا تخمّن أي رقم أو حالة شحنة.
        - اعتمد على الأدوات وبيانات API.
        - لا تستخدم أداة تنفيذية إذا كان الطلب غامضًا.
        - لا تلغي شحنة إلا إذا ذكر المستخدم سبب الإلغاء.
        - إذا حاول المستخدم حذف شحنة نهائيًا، وضّح أن النظام يستخدم إلغاءً آمنًا soft cancellation بدل الحذف النهائي.
        - اجعل الإجابة بالعربية، مختصرة، عملية، ومناسبة لفريق الإدارة.
    
        شكل الإجابة:
        - اكتب answer كملخص واضح لما حدث أو لما وجدته.
        - املأ used_data_sources بأسماء الأدوات أو مسارات API المستخدمة.
        - أضف key_metrics عند وجود أرقام مهمة.
        - أضف operational_insights عند وجود مشكلة تشغيلية أو ملاحظة مهمة.
        - أضف proposed_actions عند وجود إجراء مقترح أو خطوة متابعة.
    

"""


)









# Read Tools




@shipping_agent.tool
def get_management_overview(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
      تجلب هذه الأداة ملخصًا إداريًا عامًا عن حالة شركة التوصيل،
         مثل عدد الشحنات، حالات التسليم، التأخير، المرتجعات،
         الشحنات الملغاة، الإيرادات المحصلة، والإيرادات المعلقة.
         استخدم هذه الأداة عندما يسأل المستخدم عن ملخص الشركة أو التقرير التنفيذي.
             
    
    """
    try:
        return to_json(ctx.deps.api.get_mangement_overview())

    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def get_shipments(ctx: RunContext[ShippingAgentDeps], status: str | None = None, branch_name:str |None = None,) -> str:
    """
     
     تجلب هذه الأداة قائمة الشحنات مع إمكانية استخدام فلاتر اختيارية حسب الحالة واسم الفرع.
        الحالات المسموحة هي: delivered, in_transit, delayed, returned, cancelled.
        استخدم هذه الأداة عندما يسأل المستخدم عن قائمة الشحنات أو عن بيانات شحنات مفلترة.
    
    
    

    """

    try:
        data = ctx.deps.api.get_shipments(status = status, branch_name=branch_name)
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def get_shipment_by_id(ctx: RunContext[ShippingAgentDeps], shipment_id: str) -> str:
    """
     تجلب هذه الأداة تفاصيل شحنة واحدة باستخدام رقم الشحنة.
        استخدم هذه الأداة عندما يسأل المستخدم عن شحنة محددة مثل SHP-1020.
        
    
    
    """
    try:
        return to_json(ctx.deps.api.get_shipments_by_id(shipment_id))
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def get_payments_summary(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
     تجلب هذه الأداة ملخص المدفوعات، بما في ذلك المبالغ المدفوعة،
        والمبالغ المعلقة، والمبالغ المستردة.
    
        استخدم هذه الأداة عندما يسأل المستخدم عن الإيرادات،
        أو التحصيل، أو المدفوعات المعلقة، أو المبالغ المستردة،
        أو الملخص المالي.
    
    

    """
    try:
        return to_json(ctx.deps.api.get_payments_summary())
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"




@shipping_agent.tool
def get_delayed_shipments(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
    
     تجلب هذه الأداة جميع الشحنات المتأخرة.
        استخدم هذه الأداة عندما يسأل المستخدم عن الشحنات المتأخرة،
        أو التأخير في التسليم، أو مشكلات التأخير التشغيلية،
        أو الفروع المتأثرة بالتأخير.
    
    
    
    """

    try:
        return to_json(ctx.deps.api.get_delayed_shipments())

    except ShippingAPIError as error:
        return f"API_Error: {error}"
    



@shipping_agent.tool
def get_returned_shipments(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
     تجلب هذه الأداة الشحنات المرتجعة.
        استخدم هذه الأداة عندما يسأل المستخدم عن الشحنات التي رجعت
        أو عن عدد الشحنات المرتجعة أو تفاصيلها.
    
    
    
    """

    try:
        return to_json(ctx.deps.api.get_returned_shipments())
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def get_returns(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
     تجلب هذه الأداة سجلات المرتجعات مع أسباب الإرجاع وقيم الاسترداد.
        استخدم هذه الأداة عندما يسأل المستخدم عن أسباب المرتجعات،
        أو مشكلات الإرجاع، أو المبالغ المستردة، أو تحليل المرتجعات.
    
    
    """
    try:
        return to_json(ctx.deps.api.get_returns())

    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def get_branches_performance(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
     تجلب هذه الأداة مؤشرات أداء الفروع، مثل عدد الشحنات الكلي،
        وعدد الشحنات المسلمة، والمتأخرة، والمرتجعة، والملغاة،
        والإيرادات المحصلة لكل فرع.
    
        استخدم هذه الأداة عندما يسأل المستخدم عن أفضل الفروع،
        أو أضعف الفروع، أو مقارنة الفروع، أو التأخير حسب الفرع،
        أو المرتجعات حسب الفرع، أو الإيرادات حسب الفرع.
    
    
    """

    try:
        return to_json(ctx.deps.api.get_branches_performance())

    except ShippingAPIError as error:
        return f"API_ERROR: {error}"






@shipping_agent.tool
def get_executive_report_data(ctx: RunContext[ShippingAgentDeps]) -> str:
    """
     تجمع هذه الأداة البيانات الأساسية اللازمة لبناء تقرير تنفيذي عن وضع الشركة.
        تشمل البيانات: الملخص الإداري العام، ملخص المدفوعات، أداء الفروع،
        الشحنات المتأخرة، وسجلات المرتجعات.
    
        استخدم هذه الأداة عندما يطلب المستخدم تقريرًا تنفيذيًا،
        أو ملخصًا إداريًا شاملًا، أو نظرة عامة تساعد الإدارة على اتخاذ قرار.
    
    
    
    """

    try:
        data = {

            "mangement_overview": ctx.deps.api.get_mangement_overview(),
            "payments_summary": ctx.deps.api.get_payments_summary(),
            "branches_performence": ctx.deps.api.get_branches_performance(),
            "delayed_shipments": ctx.deps.api.get_delayed_shipments(),
            "returns": ctx.deps.api.get_returns(),

        }

        return to_json(data)

    except ShippingAPIError as error:
        return f"API_ERROR: {error}"






@shipping_agent.tool
def create_shipment(

    ctx: RunContext[ShippingAgentDeps],
    customer_id: str,
    customer_name: str,
    branch_id: str,
    branch_name: str,
    origin_city: str,
    destination_city: str,
    expected_delivery: str,
    amount: float,
    weight_kg: float,

) -> str:
    """
     تنشئ هذه الأداة شحنة جديدة من خلال Shipping API.
    
        الحقول المطلوبة:
        customer_id, customer_name, branch_id, branch_name, origin_city,
        destination_city, expected_delivery, amount, weight_kg.
    
        استخدم هذه الأداة عندما يطلب المستخدم إنشاء شحنة جديدة
        وتكون جميع البيانات المطلوبة متوفرة.
            
    
    """
    shipment_data = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "branch_id": branch_id,
        "branch_name": branch_name,
        "origin_city": origin_city,
        "destination_city": destination_city,
        "expected_delivery": expected_delivery,
        "amount": amount,
        "weight_kg":weight_kg,
        

    }


    try:
        return to_json(ctx.deps.api.create_shipment(shipment_data))
    except ShippingAPIError as error:
        return f"API_ERROR: {error}" 



@shipping_agent.tool
def update_shipment(

    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    customer_name: str | None = None,
    destination_city: str | None = None,
    expected_delivery: str | None =None,
    amount: float | None = None,
    weight_kg: float  | None = None
) -> str:
    """
     تعدل هذه الأداة الحقول القابلة للتعديل في شحنة موجودة.
    
        الحقول القابلة للتعديل:
        customer_name, destination_city, expected_delivery, amount, weight_kg.
    
        استخدم هذه الأداة عندما يطلب المستخدم تعديل بيانات شحنة
        ويحدد رقم الشحنة والحقول التي يريد تعديلها.
        
    
    """

    updates = {

        "shipment_id": shipment_id,
        "customer_name": customer_name,
        "destination_city": destination_city,
        "expected_delivery": expected_delivery,
        "amount": amount,
        "weight_kg": weight_kg,


    }


    updates = {

        key: value
        for key, value in updates.items()
        if value is not None


    }

    if not updates:
        return "NO_UPDATES_PROVIDE"

    try:
        data = ctx.deps.api.update_shipment(
            shipment_id= shipment_id,
            updates=updates,

        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def change_shipment_status(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    status: str,

) -> str:

    """
    
     تغيّر هذه الأداة حالة شحنة موجودة.
    
        الحالات المسموحة:
        delivered, in_transit, delayed, returned, cancelled.
    
        استخدم هذه الأداة عندما يطلب المستخدم تغيير حالة شحنة.
    
    
    """

    allowed_status = {

        "delivered",
        "in_transit",
        "delyed",
        "returned",
        "cancelled",


    }

    status = status.strip().lower()

    if status not in allowed_status:
        return f"INVALID_STSTUS. Allowed Status: {', '.join(sorted(allowed_status))}"        


    try:
        data = ctx.deps.api.change_shipment_status(
            shipment_id = shipment_id,
            status=status, 

        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def reschedule_shipment(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    expected_delivery: str,


) ->str:
    """
    
     تعيد هذه الأداة جدولة موعد التسليم المتوقع لشحنة.
    
        استخدم هذه الأداة عندما يطلب المستخدم تغيير موعد التسليم،
        أو تأجيله، أو إعادة جدولة تاريخ التسليم المتوقع.
    
    
    """

    try:
        data = ctx.deps.api.reschedule_shipment(
            shipment_id=shipment_id,
            expected_deivery=expected_delivery,


        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"



@shipping_agent.tool
def cancel_shipment(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    reason: str,

) -> str:
    """
    
     تلغي هذه الأداة شحنة مع تسجيل سبب واضح للإلغاء.
        هذا الإلغاء آمن soft cancellation، وليس حذفًا نهائيًا من النظام.
        استخدم هذه الأداة فقط عندما يطلب المستخدم إلغاء شحنة
        ويذكر سبب الإلغاء.
        إذا لم يذكر المستخدم سبب الإلغاء، اسأله عنه ولا تخترع سببا.
    
    """

    reason = reason.strip()

    if not reason:
        return "CANCELLATION_REASON_REQUIRED!"

    try:
        data = ctx.deps.api.cancel_shipment(
            shipment_id=shipment_id,
            reason=reason,


        )
        return to_json(data)

    except ShippingAPIError as error:
        return f"API_ERROR: {error}"





@shipping_agent.tool
def draft_follow_up_message(
    ctx: RunContext[ShippingAgentDeps],
    target: str,
    reason: str,

) -> str:


    """
    
     تجهز هذه الأداة مسودة رسالة متابعة آمنة لفرع أو فريق داخلي.
    
        هذه الأداة لا ترسل الرسالة فعليًا، بل تجهز مسودة فقط
        حتى يراجعها الإنسان قبل الإرسال.
    
        استخدم هذه الأداة عندما يطلب المستخدم إشعار فرع،
        أو متابعة فريق داخلي، أو تجهيز رسالة عن التأخير،
        أو المرتجعات، أو الأعمال المعلقة.
        
    
    """

    message = {
        "target": target,
        "reason": reason,
        "requires_human_approval": True,
        "draft_message": 

            f"يرجى مراجعة الحالة التالية: {reason}. "
                        "نحتاج إلى تحديث واضح قبل نهاية اليوم مع توضيح سبب التأخير أو المشكلة والإجراء المتخذ."
                    ,
        }




    
    return to_json(message)


def create_agent_deps() -> ShippingAgentDeps:
    return ShippingAgentDeps(
        api=ShippingAPIClient.from_env(),



    )
