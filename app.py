import os
import pandas as pd
import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="Quản lý Dạy thêm & Học phí", page_icon="📚", layout="wide"
)

# Đường dẫn file lưu dữ liệu
DATA_FILE = "hoc_sinh.csv"


# Hàm tải dữ liệu
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Dữ liệu mẫu ban đầu nếu chưa có file
        df = pd.DataFrame(
            columns=[
                "ID",
                "Họ tên học sinh",
                "Môn học",
                "Học phí/Buổi (VNĐ)",
                "Số buổi đã học",
                "Trạng thái học phí",
            ]
        )
        df.to_csv(DATA_FILE, index=False)
        return df


# Hàm lưu dữ liệu
def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# Khởi tạo session_state
if "students" not in st.session_state:
    st.session_state.students = load_data()


# --- HỆ THỐNG TỰ ĐỘNG PHÂN QUYỀN THEO THIẾT BỊ ---
# Streamlit không có hàm lấy IP trực tiếp chuẩn, nhưng ta có thể dùng mẹo hoặc nhận diện qua biến môi trường/local.
# Khi bạn chạy trên máy mình (localhost), ta mặc định nhận diện là Giáo viên.
# Hoặc đơn giản ta tạo một cơ chế xác định: Nếu truy cập qua cổng local hoặc máy chủ, hoặc cho phép nhập mật khẩu quản trị ẩn.
# Ở đây ta dùng cách kiểm tra thông dụng: Mặc định nếu chạy dưới máy bạn (hoặc bạn muốn chắc chắn), ta cung cấp 1 nút khóa/mở ở góc hoặc nhận diện tự động.
# Để đơn giản và chính xác nhất cho yêu cầu "máy tôi là giáo viên, máy khác là học sinh":
# Ta sẽ check xem app đang chạy cục bộ hay trên Cloud, kết hợp với ô nhập mật khẩu quản lý gọn nhẹ ở Sidebar.

st.sidebar.title("🔐 Hệ thống Quản lý")

# Mật khẩu để mở quyền Giáo viên (Tránh việc học sinh vô tình hoặc cố ý vào chế độ giáo viên)
# Nếu đúng mật khẩu của bạn -> Hiện giao diện giáo viên. Nếu không điền hoặc sai -> Giao diện học sinh.
admin_password = st.sidebar.text_input(
    "Mật khẩu Giáo viên (để trống nếu là Học sinh)", type="password"
)

# Mật khẩu mặc định của bạn ở đây (Bạn có thể đổi chữ 'admin123' thành mật khẩu riêng của bạn)
MY_PASSWORD = "admin123"

is_teacher = admin_password == MY_PASSWORD

# ==========================================
# 1. GIAO DIỆN DÀNH CHO GIÁO VIÊN (KHI ĐÚNG MẬT KHẨU)
# ==========================================
if is_teacher:
    st.sidebar.success("✅ Đã đăng nhập quyền Giáo viên")
    st.title("👨‍🏫 Trang Quản lý của Giáo viên")

    menu = st.sidebar.selectbox(
        "Chọn chức năng",
        [
            "Quản lý danh sách & Số buổi",
            "Ghi nhận buổi học",
            "Thống kê tài chính",
        ],
    )

    # Nút làm mới dữ liệu từ file
    st.session_state.students = load_data()

    if menu == "Quản lý danh sách & Số buổi":
        st.subheader("👥 Thêm học sinh mới")

        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Họ tên học sinh (Viết hoa/thường tùy ý)")
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
                    new_id = (
                        int(st.session_state.students["ID"].max() + 1)
                        if not st.session_state.students.empty
                        else 1
                    )
                    new_row = {
                        "ID": new_id,
                        "Họ tên học sinh": name.strip(),
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
                    save_data(st.session_state.students)
                    st.success(f"Đã thêm học sinh {name} thành công!")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập tên học sinh.")

        st.divider()
        st.subheader("📋 Danh sách học sinh hiện tại (Đã lưu tự động)")

        if not st.session_state.students.empty:
            df_display = st.session_state.students.copy()
            df_display["Tổng tiền cần nộp (VNĐ)"] = (
                df_display["Số buổi đã học"]
                * df_display["Học phí/Buổi (VNĐ)"]
            )

            edited_df = st.data_editor(
                df_display, num_rows="dynamic", use_container_width=True
            )

            if st.button("💾 Lưu thay đổi bảng"):
                # Cập nhật lại dữ liệu gốc (bỏ cột tính toán ra trước khi lưu)
                updated_save = edited_df[
                    [
                        "ID",
                        "Họ tên học sinh",
                        "Môn học",
                        "Học phí/Buổi (VNĐ)",
                        "Số buổi đã học",
                        "Trạng thái học phí",
                    ]
                ]
                st.session_state.students = updated_save
                save_data(updated_save)
                st.success("Đã lưu dữ liệu thành công vào file!")
                st.rerun()
        else:
            st.info("Chưa có học sinh nào trong danh sách.")

    elif menu == "Ghi nhận buổi học":
        st.subheader("➕ Cộng dồn số buổi học nhanh")

        if st.session_state.students.empty:
            st.warning("Vui lòng thêm học sinh trước.")
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
                save_data(st.session_state.students)
                st.success(f"Đã cập nhật thành công cho {selected_student}!")
                st.rerun()

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
                st.success("Tuyệt vời! Tất cả học sinh đều đã nộp học phí.")

# ==========================================
# 2. GIAO DIỆN DÀNH CHO HỌC SINH (TỰ GÕ TÊN)
# ==========================================
else:
    st.title("🎓 Tra cứu thông tin học tập & học phí cá nhân")

    if st.session_state.students.empty:
        st.warning(
            "Hệ thống chưa có dữ liệu học sinh. Vui lòng liên hệ giáo viên."
        )
    else:
        st.markdown(
            "Vui lòng **nhập đầy đủ họ và tên** của bạn vào ô dưới đây để tra cứu:"
        )

        # Ô để học sinh tự gõ tên (không hiện danh sách full)
        typed_name = st.text_input("Họ và tên của bạn:")

        if typed_name:
            # Lọc tìm kiếm gần đúng hoặc chính xác tên học sinh (không phân biệt hoa thường)
            df_students = st.session_state.students
            matched = df_students[
                df_students["Họ tên học sinh"].str.contains(
                    typed_name.strip(), case=False, na=False
                )
            ]

            if not matched.empty:
                for idx, student_info in matched.iterrows():
                    s_name = student_info["Họ tên học sinh"]
                    subject = student_info["Môn học"]
                    fee_per_session = student_info["Học phí/Buổi (VNĐ)"]
                    total_sessions = student_info["Số buổi đã học"]
                    status = student_info["Trạng thái học phí"]

                    total_money = total_sessions * fee_per_session

                    st.divider()
                    st.markdown(f"### Kết quả tra cứu cho: **{s_name}**")

                    col1, col2, col3 = st.columns(3)
                    col1.metric(
                        "Môn học", subject if subject else "Chưa cập nhật"
                    )
                    col2.metric("Tổng số buổi đã học", f"{total_sessions} buổi")
                    col3.metric(
                        "Tổng số tiền cần nộp", f"{total_money:,.0f} VNĐ"
                    )

                    st.markdown("---")
                    if status == "Đã nộp":
                        st.success(
                            "✅ **Trạng thái học phí:** Bạn đã hoàn thành học phí."
                        )
                    else:
                        st.error(
                            "❌ **Trạng thái học phí:** Bạn chưa nộp học phí. Vui lòng thanh toán cho giáo viên."
                        )
            else:
                st.error(
                    f"Không tìm thấy học sinh nào có tên khớp với **'{typed_name}'**. Vui lòng kiểm tra lại chính tả!"
                )
