from multi_agents.pipeline import pipeline
from multi_agents.utils.logging import setup_logger


def main():
    logger = setup_logger()
    
    customer_query = "Tôi muốn mua iPhone 15 Pro Max 256GB màu Titan tự nhiên còn hàng không? Giá bao nhiêu? Nếu có thì tôi muốn đặt hàng ngay."

    initial_context = {
        "conversation_id": "12345",
        "customer_name": "Nguyễn Văn A",
        "previous_interactions": "Đã từng hỏi về iPad Air."
    }
    
    try:
        pipeline_output_data = pipeline(customer_query, initial_context_data=initial_context)
        
        print("\n========= KẾT QUẢ =========")
        logger.info(f"\nCâu trả lời cho khách hàng:\n{pipeline_output_data.get('customer_response')}")
        
        print(f"Response: {pipeline_output_data.get('customer_response')}")
        print(f"Task 1: {pipeline_output_data.get('task1_output')}")
        print(f"Task 2: {pipeline_output_data.get('task2_output')}")
        print(f"Task 3: {pipeline_output_data.get('task3_output')}")
        print(f"Token usage: {pipeline_output_data.get('token_usage')}")

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng trong pipeline: {e}", exc_info=True)

if __name__ == "__main__":
    main()