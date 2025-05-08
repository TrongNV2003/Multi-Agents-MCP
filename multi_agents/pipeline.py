import json
from loguru import logger
from crewai import Crew, Task, Process

from multi_agents.tools.create_order import CreateOrderTool
from multi_agents.agents.agents import ConsultantAgent, InventoryAgent, OrderAgent

def pipeline(customer_input: str, initial_context_data: dict = None):
    logger.info(f"Pipeline started with input: '{customer_input}' and context: {initial_context_data}")

    tools_for_order_agent = [CreateOrderTool()]

    consultant = ConsultantAgent()
    inventory = InventoryAgent()
    order = OrderAgent(tools=tools_for_order_agent)

    # Task 1: Consultant Agent phân tích yêu cầu
    task1_analyze_request = Task(
        description=f"""Phân tích kỹ lưỡng yêu cầu của khách hàng: '{customer_input}'.
        Xác định các thông tin quan trọng như:
        1. Tên sản phẩm hoặc loại sản phẩm khách hàng quan tâm.
        2. Ý định chính của khách hàng (ví dụ: hỏi thông tin, kiểm tra tồn kho, hỏi giá, muốn đặt hàng).
        3. Bất kỳ chi tiết cụ thể nào khác (màu sắc, dung lượng, v.v.).

        Dựa trên phân tích, hãy chuẩn bị một bản tóm tắt rõ ràng.
        Nếu khách hàng cung cấp thông tin trong 'initial_context_data' (nếu có): {initial_context_data}, hãy kết hợp nó.
        - Nếu khách hàng đề cập đến từ "muốn mua", "đặt mua", hoặc tương tự, hãy đánh giá là họ có ý định đặt hàng (requires_order_placement=true).

        CHÚ Ý:
        - Phản hồi của bạn PHẢI là một đối tượng JSON thuần túy, KHÔNG bao gồm bất kỳ định dạng markdown nào như ```json hoặc ```. 
        - Chỉ trả về đối tượng JSON với các trường như mô tả, không thêm văn bản trước hoặc sau JSON.
        """,
        agent=consultant.crewai_agent,
        expected_output="Một đối tượng JSON thuần túy (không bọc trong markdown) chứa: "
                        "'product_details': (string) mô tả sản phẩm khách quan tâm (ví dụ: 'iPhone 13 128GB màu xanh'), "
                        "'customer_intent': (string) ý định của khách (ví dụ: 'check_inventory_price', 'place_order', 'general_query'), "
                        "'original_query': (string) câu hỏi gốc của khách hàng, "
                        "'requires_inventory_check': (boolean) liệu có cần kiểm tra kho/giá không, "
                        "'requires_order_placement': (boolean) liệu khách có ý định đặt hàng không."
    )

    # Task 2: Inventory Agent kiểm tra kho và giá (phụ thuộc vào Task 1)
    task2_check_inventory = Task(
        description=f"""Dựa trên kết quả phân tích từ Task 1 (đặc biệt là 'product_details' và 'requires_inventory_check'):
        - Nếu 'requires_inventory_check' là true và 'product_details' có thông tin:
          Hãy sử dụng các công cụ/kiến thức của bạn để kiểm tra tình trạng tồn kho và giá của sản phẩm.
          Sản phẩm cần kiểm tra sẽ được cung cấp từ output của Task 1.
        - Nếu 'requires_inventory_check' là false hoặc không có thông tin sản phẩm rõ ràng:
          Trả về thông báo cho biết không cần kiểm tra kho hoặc không đủ thông tin.
        
        CHÚ Ý:
        - Phản hồi của bạn PHẢI là một đối tượng JSON thuần túy, KHÔNG bao gồm bất kỳ định dạng markdown nào như ```json hoặc ```. 
        - Chỉ trả về đối tượng JSON với các trường như mô tả, không thêm văn bản trước hoặc sau JSON.
        """,
        agent=inventory.crewai_agent,
        expected_output="Một đối tượng JSON thuần túy (không bọc trong markdown) chứa: "
                        "'product_name': (string) tên sản phẩm đã kiểm tra, "
                        "'stock_status': (string) 'in_stock', 'out_of_stock', 'low_stock', hoặc 'not_checked', "
                        "'price': (number) giá sản phẩm (nếu có và đã kiểm tra), "
                        "'message': (string) thông báo bổ sung (ví dụ: 'Không đủ thông tin để kiểm tra').",
        context=[task1_analyze_request]
    )

    # Task 3: Order Agent xử lý việc đặt hàng (phụ thuộc vào Task 1 và Task 2)
    task3_place_order = Task(
        description=f"""Dựa trên kết quả phân tích từ Task 1 ('customer_intent', 'requires_order_placement', 'product_details')
        và kết quả kiểm tra kho từ Task 2 ('stock_status', 'price'):
        - Nếu 'requires_order_placement' là true, sản phẩm có trong kho ('in_stock' hoặc 'low_stock'), và có đủ thông tin:
          1. Tạo một `order_id` duy nhất cho đơn hàng (ví dụ: sử dụng UUID dạng chuỗi).
          2. Tạo một cấu trúc JSON dạng Dictionary chi tiết cho đơn hàng. JSON này phải bao gồm:
             - `order_id`: (string) ID vừa tạo.
             - `product`: (string) Tên sản phẩm từ Task 2.
             - `quantity`: (number) Mặc định là 1, hoặc nếu khách hàng chỉ định.
             - `total_price`: (number) Giá sản phẩm từ Task 2.
             - `customer_info`: một object chứa thông tin khách hàng từ `initial_context_data`: {initial_context_data} (bao gồm `customer_name` và `conversation_id`).
          3. Đặt `order_created` là True.
        - Nếu không đủ điều kiện đặt hàng (ví dụ: khách không muốn đặt, hết hàng, thiếu thông tin):
          Đặt `order_created` là False và cung cấp `message` giải thích.

        CHÚ Ý: 
        - Phản hồi của bạn PHẢI là một đối tượng JSON thuần túy, KHÔNG bao gồm bất kỳ định dạng markdown nào như ```json hoặc ```. 
        - Chỉ trả về đối tượng JSON với các trường như mô tả, không thêm văn bản trước hoặc sau JSON.
        """,
        agent=order.crewai_agent,
        expected_output="Một đối tượng JSON thuần túy (không bọc trong markdown) chứa: "
                        "'order_created': (boolean) đơn hàng có được tạo không, "
                        "'order_details': (object) chi tiết đơn hàng nếu được tạo (ví dụ: {'order_id', 'product', 'quantity', 'total_price', 'customer_info'}), "
                        "'message': (string) thông báo về trạng thái tạo đơn hàng.",
        context=[task1_analyze_request, task2_check_inventory]
    )

    # Task 4: Consultant Agent tổng hợp và tạo phản hồi cuối cùng cho khách hàng
    task4_final_response = Task(
        description=f"""Tổng hợp tất cả thông tin từ các bước trước:
        - Phân tích yêu cầu ban đầu (từ Task 1).
        - Kết quả kiểm tra kho/giá (từ Task 2).
        - Tình trạng xử lý đơn hàng (từ Task 3).

        Dựa trên toàn bộ quá trình, hãy soạn một câu trả lời hoàn chỉnh, thân thiện và chính xác cho câu hỏi ban đầu của khách hàng: '{customer_input}'.
        Nếu có bất kỳ vấn đề hoặc thông tin nào không rõ ràng, hãy giải thích một cách lịch sự.
        """,
        agent=consultant.crewai_agent,
        expected_output="Một chuỗi (string) là câu trả lời cuối cùng bằng ngôn ngữ tự nhiên để gửi cho khách hàng.",
        context=[task1_analyze_request, task2_check_inventory, task3_place_order]
    )

    sales_crew = Crew(
        agents=[consultant.crewai_agent, inventory.crewai_agent, order.crewai_agent],
        tasks=[task1_analyze_request, task2_check_inventory, task3_place_order, task4_final_response],
        process=Process.sequential,
        verbose=True
    )

    logger.info("Kicking off the crew...")
    final_result = sales_crew.kickoff()

    logger.info(f"Crew execution finished. Final result: {final_result}")

    customer_response_str = ""
    if hasattr(final_result, 'raw') and final_result.raw is not None:
        customer_response_str = str(final_result.raw)
    elif hasattr(final_result, 'result') and final_result.result is not None:
        customer_response_str = str(final_result.result)
    else:
        last_task_output = task4_final_response.output
        if last_task_output and hasattr(last_task_output, 'raw'):
            customer_response_str = str(last_task_output.raw)
        else:
            customer_response_str = "Không thể trích xuất phản hồi cuối cùng từ CrewOutput."
            logger.warning("Could not extract a serializable string from CrewOutput or the last task.")

    task1_res = task1_analyze_request.output
    task2_res = task2_check_inventory.output
    task3_res = task3_place_order.output
    
    pipeline_result_dict = {
        "customer_response": customer_response_str,
        "task1_output": str(task1_res.raw) if task1_res and hasattr(task1_res, 'raw') else "Task 1: Output không có hoặc không có thuộc tính .raw",
        "task2_output": str(task2_res.raw) if task2_res and hasattr(task2_res, 'raw') else "Task 2: Output không có hoặc không có thuộc tính .raw",
        "task3_output": str(task3_res.raw) if task3_res and hasattr(task3_res, 'raw') else "Task 3: Output không có hoặc không có thuộc tính .raw",
        "token_usage": getattr(final_result, 'token_usage', None) if hasattr(final_result, 'token_usage') else "Không có thông tin token usage"
    }

    for key, value in pipeline_result_dict.items():
        if not isinstance(value, (str, int, float, list, dict, bool, type(None))):
            logger.warning(f"Giá trị cho key '{key}' có kiểu {type(value)} không thể serialize JSON trực tiếp, chuyển thành string: {str(value)[:200]}")
            pipeline_result_dict[key] = str(value)

    return pipeline_result_dict

if __name__ == "__main__":
    customer_query = "Tôi muốn mua iPhone 15 Pro Max 256GB màu Titan tự nhiên còn hàng không? Giá bao nhiêu? Nếu có thì tôi muốn đặt hàng ngay."

    initial_context = {
        "conversation_id": "12345",
        "customer_name": "Nguyễn Văn A",
        "previous_interactions": "Đã từng hỏi về iPad Air."
    }
    
    try:
        pipeline_output_data = pipeline(customer_query, initial_context_data=initial_context)
        
        print("\n========= KẾT QUẢ =========")
        for key, value in pipeline_output_data.items():
            value_repr = str(value)
            if len(value_repr) > 200: value_repr = value_repr[:200] + "..."
            print(f"  {key}: ({type(value).__name__}) {value_repr}")

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng trong pipeline: {e}", exc_info=True)