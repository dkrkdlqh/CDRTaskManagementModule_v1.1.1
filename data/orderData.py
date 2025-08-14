from cdrutils.log import CDRLog
class OrderItem:
    """
    OrderItem 클래스는 한 주문의 menuId, orderState, printState를 관리합니다.
    """
    def __init__(self, orderId: int, orderNumber: int, menuId: int, orderPhoneInfo: str, mbrushPrintType: str):
        # server에서 받은 주문 정보
        # key값은 orderId
        self.orderId = orderId  ####          
        self.orderNumber = orderNumber
        self.orderPhoneInfo   = orderPhoneInfo
        self.mbrushPrintType  = mbrushPrintType
        self.menuId = menuId
        
        #주문 진행 상태 -1: 없음, 0: 컵 준비, 1: 추출 시작, 2: 추출 완료, 3: 픽업 가능
        self.orderState = -1
        # '''mini 임시 test'''
        # self.orderState = 0
        # ''''''
        
        # 메뉴 제조 장비 -1 : 없음, 1 : 1번 드롱기, 2 : 2번 드롱기
        self.makeMachine = -1

    def __repr__(self):
        return f"OrderItem(menuId={self.menuId}, orderState={self.orderState}, orderId={self.orderId}, orderNumber={self.orderNumber}, orderPhoneInfo={self.orderPhoneInfo}, mbrushPrintType={self.mbrushPrintType}, makeMachine={self.makeMachine})"


class OrderHandler:
    """
    OrderHandler 클래스는 여러 OrderItem 객체를 관리합니다.
    """
    def __init__(self):
        self.__OrderItems: list[OrderItem] = []

    def addOrderItem(self, orderId: int, orderNumber: int, menuId: int, orderPhoneInfo: str, mbrushPrintType: str):
        """
        새로운 OrderItem을 추가합니다.
        """
        self.__OrderItems.append(OrderItem(orderId, orderNumber, menuId, orderPhoneInfo, mbrushPrintType))
        
    
    def updateOrderState(self, orderitem: OrderItem, newState: int):
        """
        OrderItem의 orderState를 업데이트합니다.
        """
        orderitem.orderState = newState
        CDRLog.print(f"Updated orderState for OrderId {orderitem.orderId} to {newState} // Menu : {orderitem.menuId} ")

    def updateOrderStateByOrderId(self, orderId: int, newState: int):
        """
        특정 orderId를 가진 모든 OrderItem의 orderState를 일괄적으로 업데이트합니다.
        """
        updated = False
        for item in self.__OrderItems:
            if item.orderId == orderId:
                item.orderState = newState
                updated = True
        
        if not updated:
            print(f"No OrderItems found with OrderId {orderId}.")
            
    def removeOrderItem(self, orderitem: OrderItem):
        """
        특정 OrderItem 객체를 리스트에서 제거합니다.
        """
        try:
            self.__OrderItems.remove(orderitem)
            CDRLog.print(f"OrderItem with orderId {orderitem.orderId} ({orderitem.menuId}) removed successfully.")
        except ValueError:
            CDRLog.print(f"OrderItem with orderId {orderitem.orderId} ({orderitem.menuId}) not found in the list.")

    def listOrderItems(self):
        """
        현재 관리 중인 모든 OrderItem을 출력합니다.
        """
        print("=== Current Order Items ===")
        for item in self.__OrderItems:
            print(item)
        print("===========================")
    def getOrderItemById(self, orderId: int) -> OrderItem:
        """
        특정 orderId를 가진 OrderItem을 반환합니다. 없으면 None을 반환합니다.
        """
        return next((item for item in self.__OrderItems if item.orderId == orderId), None)

    def getOrderItemByState(self, state: int) -> OrderItem: ##
        """
        특정 상태(state)를 가진 OrderItem 중 orderId가 가장 작은 항목을 반환합니다.
        """
        # 상태가 state인 주문만 필터링하고, orderId 기준으로 정렬
        filtered_orders = sorted(
            (item for item in self.__OrderItems if item.orderState == state),
            key=lambda x: x.orderId
        )
        # 첫 번째 주문 반환 (없으면 None)
        return filtered_orders[0] if filtered_orders else None
    
    # def getOrderItemByIdMenuState(self, orderId: int, menuId: int, state: int) -> OrderItem:
    #     """
    #     특정 orderId, menuId, orderState를 가진 OrderItem을 반환합니다. 없으면 None을 반환합니다.
    #     """
    #     return next(
    #         (item for item in self.__OrderItems if item.orderId == orderId and item.menuId == menuId and item.orderState == state),
    #         None
    #     )
    def getOrderItemByIdAndState(self, orderId: int, state: int) -> OrderItem:
        """
        특정 orderId와 state를 모두 만족하는 OrderItem을 반환합니다. 없으면 None을 반환합니다.
        """
        return next((item for item in self.__OrderItems if item.orderId == orderId and item.orderState == state), None)
    
    def getOrderItemByIdMenuStateExcept(self, orderId: int, except_state: int) -> OrderItem:
        """
        특정 orderId를 가지면서 except_state가 아닌 orderState를 가진 OrderItem을 반환합니다. 없으면 None을 반환합니다.
        """
        return next(
            (item for item in self.__OrderItems if item.orderId == orderId  and item.orderState != except_state),
            None
        )


    def getOrderCount(self) -> int:
        """
        현재 저장된 OrderItem의 개수를 반환합니다.
        """
        return len(self.__OrderItems)
    
    def getMenuIdsByOrderId(self, orderId: int) -> list[int]:
        """
        특정 orderId를 가진 OrderItem들의 menuId를 리스트로 반환합니다.
        """
        return [item.menuId for item in self.__OrderItems if item.orderId == orderId]
# # 테스트 코드
# if __name__ == "__main__":
#     manager = OrderManager()

#     # 메뉴 추가
#     manager.addOrderItem(menuId=1000, orderState=-1, printState=False)
#     manager.addOrderItem(menuId=1001, orderState=0, printState=True)

#     # 메뉴 리스트 출력
#     print("=== Current Menu Items ===")
#     manager.listOrderItems()

#     # 특정 메뉴 찾기
#     print("\n=== Find OrderItem with menuId 1000 ===")
#     item = manager.findOrderItemById(1000)
#     print(item)

#     # 메뉴 상태 업데이트
#     print("\n=== Update orderState for menuId 1000 ===")
#     manager.updateorderState(menuId=1000, newState=1)

#     # 메뉴 리스트 출력
#     print("\n=== Current Menu Items After Update ===")
#     manager.listOrderItems()

#     # 메뉴 제거
#     print("\n=== Remove OrderItem with menuId 1001 ===")
#     manager.removeOrderItem(menuId=1001)

#     # 메뉴 리스트 출력
#     print("\n=== Current Menu Items After Removal ===")
#     manager.listOrderItems()