import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_checkout_and_qr_voucher_generation():
    # 1. Create a trip with booking
    resp_plan = client.post("/api/v1/agent/plan-trip", json={
        "prompt": "Đi du lịch Đà Lạt 3 ngày 2 đêm ngân sách 8 triệu cho 2 người"
    })
    assert resp_plan.status_code == 200
    data = resp_plan.json()
    trip_id = data["trip_id"]
    assert trip_id is not None
    assert "critique_feedback" in data
    assert "fatigue_score" in data["critique_feedback"]

    # 2. Query bookings for this trip
    resp_bks = client.get(f"/api/v1/bookings/?trip_id={trip_id}")
    assert resp_bks.status_code == 200
    bookings = resp_bks.json()
    assert len(bookings) > 0

    first_booking = bookings[0]
    b_id = first_booking["id"]

    # 3. Checkout with VNPAY
    resp_pay = client.post("/api/v1/bookings/checkout", json={
        "booking_id": b_id,
        "payment_method": "VNPAY",
        "card_number": "9704229988776655",
        "card_holder": "NGUYEN VAN A"
    })
    assert resp_pay.status_code == 200
    pay_data = resp_pay.json()
    assert pay_data["success"] is True
    assert pay_data["status"] == "CONFIRMED"
    assert "TXN-VNPAY" in pay_data["transaction_id"]
    assert "qr_code_url" in pay_data
    assert "voucher_code" in pay_data

def test_collaboration_group_and_splitwise_expenses():
    # 1. Plan trip
    resp_plan = client.post("/api/v1/agent/plan-trip", json={
        "prompt": "Du lịch Nha Trang 4 ngày 3 đêm cho nhóm bạn 4 người ngân sách 20 triệu"
    })
    trip_id = resp_plan.json()["trip_id"]

    # 2. Invite members
    resp_inv1 = client.post(f"/api/v1/trips/{trip_id}/members", json={
        "email": "lan.anh@example.com",
        "full_name": "Lan Anh",
        "role": "EDITOR"
    })
    assert resp_inv1.status_code == 200
    assert resp_inv1.json()["success"] is True

    resp_inv2 = client.post(f"/api/v1/trips/{trip_id}/members", json={
        "email": "minh.tri@example.com",
        "full_name": "Minh Trí",
        "role": "VIEWER"
    })
    assert resp_inv2.status_code == 200

    # 3. Get members
    resp_members = client.get(f"/api/v1/trips/{trip_id}/members")
    assert resp_members.status_code == 200
    members_data = resp_members.json()["members"]
    assert len(members_data) >= 3  # Owner + 2 invited

    # 4. Record shared expenses
    # Lan Anh pays 600,000 VND for dinner split among all
    resp_exp1 = client.post(f"/api/v1/trips/{trip_id}/expenses", json={
        "payer_name": "Lan Anh",
        "title": "Bữa tối hải sản Nha Trang",
        "category": "food",
        "amount": 600000.0,
        "split_members": ["Lan Anh", "Minh Trí", "Trưởng đoàn"]
    })
    assert resp_exp1.status_code == 200

    # Trưởng đoàn pays 300,000 VND for taxi split between Lan Anh and Trưởng đoàn
    resp_exp2 = client.post(f"/api/v1/trips/{trip_id}/expenses", json={
        "payer_name": "Trưởng đoàn",
        "title": "Taxi di chuyển Tháp Bà Ponagar",
        "category": "transit",
        "amount": 300000.0,
        "split_members": ["Lan Anh", "Trưởng đoàn"]
    })
    assert resp_exp2.status_code == 200

    # 5. Get expenses and debt settlement summary
    resp_exp_list = client.get(f"/api/v1/trips/{trip_id}/expenses")
    assert resp_exp_list.status_code == 200
    exp_summary = resp_exp_list.json()
    assert exp_summary["total_spent"] == 900000.0
    assert "balances" in exp_summary
    assert "debt_settlements" in exp_summary
    assert isinstance(exp_summary["debt_settlements"], list)
