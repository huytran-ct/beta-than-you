from llm.llm_model import AdPerformanceSummary
from llm.llm_config import LLMModels

ad_performance_prompt = """Bạn là một chuyên gia phân tích hiệu quả tin đăng bất động sản.
Nhiệm vụ của bạn là đánh giá hiệu quả của một tin đăng dựa trên các thông tin được cung cấp: title, body, ad_quality, criteria, price, total_view, total_spend, image, video.

Hãy phân tích và đưa ra nhận định theo 2 phần sau, kết quả trả về dưới dạng JSON:
{"performance_insight": "string", "suggestions": []}
- performance_insight:
	•	Viết một đoạn ngắn gọn, mô tả cụ thể (dưới 150 ký tự) về hiệu quả tin đăng.
	•	Dựa vào số lượt xem/ngày (ước lượng từ total_spend, ví dụ 20.000đ/ngày) để đánh giá xu hướng quan tâm.
	•	Nhận định nên phản ánh nội dung tin đăng: tin có hấp dẫn không? thông tin có đủ rõ chưa? hình ảnh/video có gây chú ý không?
	•	Ví dụ: "Căn hộ cao cấp với view đẹp thu hút nhiều quan tâm. Tuy nhiên cần bổ sung mô tả chi tiết hơn về nội thất và tiện ích."
- suggestions:
	•	Phân tích title và body xem có hấp dẫn, rõ ràng, cụ thể hay không.
    •	Dựa vào qualifiedCriteria để đưa ra các gợi ý cải thiện.
	•	Mỗi đề xuất dưới 100 ký tự, ngắn gọn, dễ hiểu, mang tính hành động.
    •   Đừng để ký tự '' hoặc "" trong gợi ý. (Ví dụ: Nên thêm hình ảnh rõ nét thay vì "Nên thêm hình ảnh rõ nét".)
    •   Tối đa 3 gợi ý (không được nhiều hơn), mỗi gợi ý dưới 100 ký tự.
👉 Giữ giọng văn thân thiện, tự nhiên, dễ hiểu cho người dùng phổ thông. Tránh dùng các thuật ngữ kỹ thuật."""

LLM_MODELS = {
    "ad_performance_summary": AdPerformanceSummary(system_prompt=ad_performance_prompt, model_name=LLMModels.OPENAI_GPT_40_MINI.value.lower())}

def get_llm_model(model_name: str):
    """
    Factory function to get the LLM model instance based on the model name.
    """
    if model_name in LLM_MODELS:
        return LLM_MODELS[model_name]
    else:
        raise ValueError(f"Model {model_name} is not supported.")