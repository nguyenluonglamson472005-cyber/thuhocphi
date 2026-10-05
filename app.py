import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Quản lý Dạy thêm & Học phí", page_icon="📚", layout="wide"
)

# Khởi tạo dữ liệu mẫu trong st.session_state nếu chưa có
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(
        columns=[
            "ID",
            "Họ tên học sinh",
            "Môn học",
            "Học phí/Buổi (VNĐ)",
            "Số buổi đã học",
            "Trạng thái học phí",
        ]
    )

# --- THANH BÊN (SIDEBAR) ĐỂ CHỌN VAI TRÒ ---
st.sidebar.title("🔐 Hệ thống Tra cứu")
role = st.sidebar.radio("Bạn là ai?", ["Giáo viên / Quản lý", "Học sinh tra cứu"])

st.sidebar.divider()

# ==========================================
# 1. GIAO DIỆN DÀNH CHO GIÁO VIÊN / QUẢN LÝ
# ==========================================
if role == "Giáo viên / Quản lý":
    st.title("👨‍🏫 Trang Quản lý của Giáo viên")

    menu = st.sidebar.selectbox(
        "Chọn chức năng",
        [
            "Quản lý danh sách & Số buổi",
            "Ghi nhận buổi học",
            "Thống kê tài chính",
        ],
    )

    if menu == "Quản lý danh sách & Số buổi":
        st.subheader("👥 Thêm học sinh mới")

        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Họ tên học sinh")
                subject = st.text_input("Môn học")
            with col2:
                fee_per_session = st.number_input(
                    "Học phí mỗi buổi (VNĐ)", min_value=0, step=50000, value=100000
                )
                initial_sessions = st.number_input(
                    "Số buổi đã học ban đầu", min_value=0, step=1, value=0
                )

            status = st.selectbox("Trạng thái học phí", ["Chưa nộp", "Đã nộp"])

            submitted = st.form_submit_button("Thêm học sinh")
            if submitted:
                if name:
                    new_id = len(st.session_state.students) + 1
                    new_row = {
                        "ID": new_id,
                        "Họ tên học sinh": name,
                        "Môn học": subject,
                        "Học phí/Buổi (VNĐ)": fee_per_session,
                        "Số buổi đã học": initial_sessions,
                        "Trạng thái học phí": status,
                    }
                    st.session_state.students = pd.concat(
                        [
                            st.session_state.students,
                            pd.DataFrame([new_row]),
                        ],
                        ignore_index=True,
                    )
                    st.success(f"Đã thêm học sinh {name} thành công!")
                else:
                    st.error("Vui lòng nhập tên học sinh.")

        st.divider()
        st.subheader("📋 Danh sách học sinh hiện tại")

        if not st.session_state.students.empty:
            df_display = st.session_state.students.copy()
            df_display["Tổng tiền cần nộp (VNĐ)"] = (
                df_display["Số buổi đã học"]
                * df_display["Học phí/Buổi (VNĐ)"]
            )

            edited_df = st.data_editor(
                df_display, num_rows="dynamic", use_container_width=True
            )
            st.session_state.students = edited_df[
                [
                    "ID",
                    "Họ tên học sinh",
                    "Môn học",
                    "Học phí/Buổi (VNĐ)",
                    "Số buổi đã học",
                    "Trạng thái học phí",
                ]
            ]
        else:
            st.info(
                "Chưa có học sinh nào trong danh sách. Hãy thêm ở khung bên trên."
            )

    elif menu == "Ghi nhận buổi học":
        st.subheader("➕ Cộng dồn số buổi học nhanh")

        if st.session_state.students.empty:
            st.warning(
                "Vui lòng thêm học sinh trước khi điểm danh/ghi nhận buổi học."
            )
        else:
            student_names = st.session_state.students[
                "Họ tên học sinh"
            ].tolist()
            selected_student = st.selectbox("Chọn học sinh", student_names)

            student_row = st.session_state.students[
                st.session_state.students["Họ tên học sinh"] == selected_student
            ].index[0]
            current_sessions = st.session_state.students.loc[
                student_row, "Số buổi đã học"
            ]

            st.info(
                f"Số buổi hiện tại của **{selected_student}**: {current_sessions} buổi"
            )

            col1, col2 = st.columns(2)
            with col1:
                add_sessions = st.number_input(
                    "Số buổi học thêm hôm nay", min_value=1, step=1, value=1
                )
            with col2:
                new_status = st.selectbox(
                    "Cập nhật trạng thái học phí mới",
                    ["Chưa nộp", "Đã nộp"],
                    index=(
                        0
                        if st.session_state.students.loc[
                            student_row, "Trạng thái học phí"
                        ]
                        == "Chưa nộp"
                        else 1
                    ),
                )

            if st.button("Cập nhật"):
                st.session_state.students.loc[
                    student_row, "Số buổi đã học"
                ] += add_sessions
                st.session_state.students.loc[
                    student_row, "Trạng thái học phí"
                ] = new_status
                st.success(
                    f"Đã cập nhật thành công cho {selected_student}! Tổng số buổi hiện tại: {st.session_state.students.loc[student_row, 'Số buổi đã học']}"
                )

    elif menu == "Thống kê tài chính":
        st.subheader("📊 Báo cáo học phí")

        if st.session_state.students.empty:
            st.info("Chưa có dữ liệu để thống kê.")
        else:
            df = st.session_state.students.copy()
            df["Tổng tiền"] = (
                df["Số buổi đã học"] * df["Học phí/Buổi (VNĐ)"]
            )

            total_students = len(df)
            total_sessions = df["Số buổi đã học"].sum()
            total_revenue_expected = df["Tổng tiền"].sum()
            collected = df[df["Trạng thái học phí"] == "Đã nộp"][
                "Tổng tiền"
            ].sum()
            pending = df[df["Trạng thái học phí"] == "Chưa nộp"][
                "Tổng tiền"
            ].sum()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng học sinh", total_students)
            col2.metric("Tổng số buổi dạy", total_sessions)
            col3.metric("Đã thu (VNĐ)", f"{collected:,.0f}")
            col4.metric("Còn thiếu (VNĐ)", f"{pending:,.0f}", delta_color="inverse")

            st.divider()
            st.subheader("⚠ Danh sách học sinh chưa nộp học phí")
            df_unpaid = df[df["Trạng thái học phí"] == "Chưa nộp"]
            if not df_unpaid.empty:
                st.dataframe(
                    df_unpaid[
                        [
                            "Họ tên học sinh",
                            "Môn học",
                            "Số buổi đã học",
                            "Học phí/Buổi (VNĐ)",
                            "Tổng tiền",
                        ]
                    ],
                    use_container_width=True,
                )
            else:
                st.success("Tuyệt vời! Tất cả học sinh đều đã hoàn thành học phí.")

# ==========================================
# 2. GIAO DIỆN DÀNH CHO HỌC SINH TRA CỨU
# ==========================================
elif role == "Học sinh tra cứu":
    st.title("🎓 Tra cứu thông tin học tập & học phí cá nhân")

    if st.session_state.students.empty:
        st.warning(
            "Hệ thống chưa có dữ liệu học sinh. Vui lòng liên hệ giáo viên."
        )
    else:
        # Chọn tên học sinh từ danh sách
        student_names = st.session_state.students["Họ tên học sinh"].tolist()
        selected_student = st.selectbox(
            "🔍 Chọn tên của bạn để xem kết quả:", student_names
        )

        if selected_student:
            # Lọc đúng dòng dữ liệu của học sinh đó
            student_info = st.session_state.students[
                st.session_state.students["Họ tên học sinh"] == selected_student
            ].iloc[0]

            subject = student_info["Môn học"]
            fee_per_session = student_info["Học phí/Buổi (VNĐ)"]
            total_sessions = student_info["Số buổi đã học"]
            status = student_info["Trạng thái học phí"]

            total_money = total_sessions * fee_per_session

            st.divider()
            st.markdown(f"### Xin chào, **{selected_student}**!")

            # Hiển thị thông tin trực quan bằng các ô metric
            col1, col2, col3 = st.columns(3)
            col1.metric("Môn học", subject if subject else "Chưa cập nhật")
            col2.metric("Tổng số buổi đã học", f"{total_sessions} buổi")
            col3.metric("Tổng số tiền cần nộp", f"{total_money:,.0f} VNĐ")

            st.markdown("---")
            # Hiển thị trạng thái học phí
            if status == "Đã nộp":
                st.success(
                    "✅ **Trạng thái học phí:** Bạn đã hoàn thành học phí cho các buổi học trên."
                )
            else:
                st.error(
                    "❌ **Trạng thái học phí:** Bạn chưa nộp học phí. Vui lòng thanh toán cho giáo viên."
                )
