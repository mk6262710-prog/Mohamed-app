import streamlit as st
import numpy as np
import sympy as sp
from scipy.integrate import quad
import plotly.graph_objects as go
import pandas as pd

# ==========================================
# === 1. إعدادات الصفحة والتنسيق (CSS) ===
# ==========================================
st.set_page_config(
    page_title="Numerical Analysis Pro", 
    page_icon="🔢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.result-card { 
    background-color: var(--secondary-background-color); 
    padding: 20px; 
    border-radius: 15px; 
    border-left: 5px solid #007bff; 
    margin-bottom: 20px; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.exact-card { border-left: 5px solid #28a745; }
.tutorial-card { 
    border-left: 5px solid #ffc107; 
    background-color: rgba(255, 193, 7, 0.1); 
}
.card-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; opacity: 0.85; }
.card-value { font-size: 28px; font-weight: bold; color: #2d82ff; }
.exact-value { color: #28a745; }
.card-subtext { font-size: 14px; margin-top: 5px; opacity: 0.75; }
div[data-testid="column"] { padding: 0 3px !important; }
.stButton > button { 
    width: 100% !important; 
    padding: 0px !important; 
    font-size: 17px !important; 
    font-weight: bold !important; 
    height: 42px !important; 
    margin-bottom: 4px !important; 
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# === 2. إدارة حالة النص والسجل والذاكرة ===
# ==========================================
if 'func_text' not in st.session_state: 
    st.session_state.func_text = "x**3 - x - 2"
if 'preset' not in st.session_state: 
    st.session_state.preset = "اختر مثالاً..."
if 'history' not in st.session_state: 
    st.session_state.history = []

def append_to_func(text): 
    st.session_state.func_text += text

def clear_func(): 
    st.session_state.func_text = ""

def backspace_func(): 
    st.session_state.func_text = st.session_state.func_text[:-1]

def apply_preset():
    p = st.session_state.preset
    if p == "تكامل: دالة أسية (جرسية)": 
        st.session_state.func_text = "exp(-x**2)"
    elif p == "تكامل: دالة مثلثية": 
        st.session_state.func_text = "x * sin(x)"
    elif p == "جذور: دالة تكعيبية": 
        st.session_state.func_text = "x**3 - x - 2"
    elif p == "جذور: دالة أسية": 
        st.session_state.func_text = "exp(-x) - x"
    elif p == "تفاضلية: دالة خطية": 
        st.session_state.func_text = "y - x**2"
    elif p == "تفاضل: دالة لوغاريتمية": 
        st.session_state.func_text = "x * log(x)"

# دالة مساعدة لتحويل النصوص الرقمية بأمان (تعالج مشكلة .2 أو المسافات)
def safe_float(val_str):
    s = str(val_str).strip().replace(' ', '').replace('^', '**')
    if s.startswith('.'):
        s = '0' + s
    elif s.startswith('-.'):
        s = '-0.' + s[2:]
    return float(sp.sympify(s, locals={'e': sp.E, 'pi': sp.pi}))

# ==========================================
# === 3. القائمة الجانبية (Sidebar) ===
# ==========================================
st.sidebar.title("🧮 الأقسام الرياضية")
app_mode = st.sidebar.radio("اختر العملية المطلوبة:", [
    "📈 التكامل العددي (Integration)", 
    "🎯 حل المعادلات (Root Finding)",
    "🧮 أنظمة المعادلات الخطية (Linear Systems)",
    "🔬 المعادلات التفاضلية (Differential Eq)",
    "📐 التفاضل العددي (Differentiation)",
    "📉 الاستيفاء وتوفيق المنحنيات (Interpolation)"
])
st.sidebar.markdown("---")

valid_preset_modes = [
    "🧮 أنظمة المعادلات الخطية (Linear Systems)", 
    "📉 الاستيفاء وتوفيق المنحنيات (Interpolation)"
]

if app_mode not in valid_preset_modes:
    st.sidebar.selectbox(
        "💡 أمثلة سريعة للتدريب:", 
        [
            "اختر مثالاً...", 
            "تكامل: دالة أسية (جرسية)", 
            "تكامل: دالة مثلثية", 
            "جذور: دالة تكعيبية", 
            "جذور: دالة أسية", 
            "تفاضلية: دالة خطية", 
            "تفاضل: دالة لوغاريتمية"
        ], 
        key='preset', 
        on_change=apply_preset
    )

# --- 🎯 إعدادات الدقة والشرح ---
st.sidebar.markdown("---")
dp = st.sidebar.slider(
    "🎯 دقة الأرقام (Decimal Places):", 
    min_value=2, max_value=12, value=6
)
show_tutorial = st.sidebar.toggle(
    "👀 وضع الشرح (إظهار خطوات التعويض)", 
    value=True
)

# --- 🕒 سجل العمليات ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🕒 سجل العمليات (History)")
if st.sidebar.button("🗑️ مسح السجل", use_container_width=True):
    st.session_state.history = []
    st.rerun()

if not st.session_state.history:
    st.sidebar.info("السجل فارغ. ابدأ الحساب الآن!")
else:
    for item in reversed(st.session_state.history):
        st.sidebar.success(item)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: gray; font-size: 12px; margin-top: 15px;'>
    <b style='color:#007bff;'>Numerical Analysis Pro Suite</b><br>
    Zagazig National University<br>
    Mechatronics Engineering Dept.<br><br>
    <i>Developed by: Eng. Mohamed Khaled</i>
</div>
""", unsafe_allow_html=True)

# === تقسيم الشاشة الأساسي ===
col_control, col_display = st.columns([1.1, 2.4])

# ==========================================
# === 4. العمود الأيسر: لوحة التحكم ===
# ==========================================
with col_control:
    st.markdown(f"### 🎛️ إعدادات {app_mode.split('(')[0]}")
    
    # -----------------------------------------------------
    # أ. مدخلات الاستيفاء (Interpolation)
    # -----------------------------------------------------
    if "Interpolation" in app_mode:
        method = st.selectbox(
            "طريقة الاستيفاء:", 
            ["لاجرانج (Lagrange)", "الفروق المقسمة لنيوتن (Newton's Divided Differences)"]
        )
        num_pts = st.number_input("عدد النقاط (n):", min_value=2, max_value=20, value=4)
        st.info("💡 يمكنك تعديل قيم الجدول أو النسخ واللصق من Excel مباشرة.")
        
        default_x = [0.0, 1.0, 2.0, 3.0] if num_pts == 4 else [float(i) for i in range(num_pts)]
        default_y = [1.0, 2.0, 5.0, 10.0] if num_pts == 4 else [float(i**2 + 1) for i in range(num_pts)]
            
        df_pts = pd.DataFrame({"X": default_x, "Y": default_y})
        edited_pts = st.data_editor(df_pts, use_container_width=True, hide_index=True)
        target_x_str = st.text_input("🎯 احسب قيمة Y عند النقطة X = (اختياري):", value="1.5")
        
    # -----------------------------------------------------
    # ب. مدخلات الأنظمة الخطية (Linear Systems)
    # -----------------------------------------------------
    elif "Linear" in app_mode:
        st.info("💡 اكتب المعادلات بأي ترتيب، وسيقوم البرنامج بترتيبها قطرياً (Diagonally Dominant) أوتوماتيكياً!")
        method = st.selectbox(
            "اختر طريقة الحل:", 
            ["جاكوبي (Jacobi)", "جاوس-سيدل (Gauss-Seidel)", "الحذف لجاوس (Gaussian Elimination)"]
        )
        n_vars = st.number_input(
            "عدد المتغيرات (المعادلات):", 
            min_value=2, max_value=50, value=3
        )
        
        default_matrix = np.zeros((n_vars, n_vars + 1))
        if n_vars == 3:
            # مصفوفة غير مرتبة عمداً لتجربة الترتيب التلقائي الذكي
            default_matrix = np.array([
                [2, 8, -1, 11], 
                [-1, 1, 4, 3], 
                [5, -1, 1, 10]
            ], dtype=float)
        else:
            for i in range(n_vars):
                default_matrix[i, i] = 10.0
                default_matrix[i, -1] = float(i + 1)
            
        cols = [f"x{i+1}" for i in range(n_vars)] + ["= b"]
        df_matrix = pd.DataFrame(default_matrix, columns=cols)
        
        st.markdown(f"**المصفوفة الموسعة $[A | b]$ ({n_vars}×{n_vars+1}):**")
        edited_df = st.data_editor(df_matrix, use_container_width=True, hide_index=True)
        
        if "Elimination" not in method:
            tol_str = st.text_input("نسبة الخطأ المقبولة (Tolerance):", value="1e-6")
        
    # -----------------------------------------------------
    # ج. مدخلات الأقسام المعتمدة على الدوال الرياضية
    # -----------------------------------------------------
    else:
        if "Differential" in app_mode:
            func_input = st.text_input(
                "المعادلة التفاضلية y' = f(x,y):", 
                key="func_text", 
                placeholder="مثال: y - x**2"
            )
        else:
            func_input = st.text_input(
                "الدالة الرياضية f(x):", 
                key="func_text", 
                placeholder="استخدم الآلة الحاسبة أو الكيبورد..."
            )
        
        with st.expander("🧮 إظهار / إخفاء الآلة الحاسبة", expanded=False):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("sin", on_click=append_to_func, args=("sin(",))
            c2.button("cos", on_click=append_to_func, args=("cos(",))
            c3.button("tan", on_click=append_to_func, args=("tan(",))
            c4.button("π", on_click=append_to_func, args=("pi",))
            c5.button("🧹", on_click=clear_func, type="secondary")
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("sin⁻¹", on_click=append_to_func, args=("asin(",))
            c2.button("cos⁻¹", on_click=append_to_func, args=("acos(",))
            c3.button("tan⁻¹", on_click=append_to_func, args=("atan(",))
            c4.button("e^( )", on_click=append_to_func, args=("exp(",))
            c5.button("√", on_click=append_to_func, args=("sqrt(",))
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("7", on_click=append_to_func, args=("7",))
            c2.button("8", on_click=append_to_func, args=("8",))
            c3.button("9", on_click=append_to_func, args=("9",))
            c4.button("DEL", on_click=backspace_func)
            c5.button("x", on_click=append_to_func, args=("x",))
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("4", on_click=append_to_func, args=("4",))
            c2.button("5", on_click=append_to_func, args=("5",))
            c3.button("6", on_click=append_to_func, args=("6",))
            c4.button("×", on_click=append_to_func, args=("*",))
            c5.button("÷", on_click=append_to_func, args=("/",))
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("1", on_click=append_to_func, args=("1",))
            c2.button("2", on_click=append_to_func, args=("2",))
            c3.button("3", on_click=append_to_func, args=("3",))
            c4.button("+", on_click=append_to_func, args=("+",))
            c5.button("-", on_click=append_to_func, args=("-",))
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.button("0", on_click=append_to_func, args=("0",))
            c2.button(".", on_click=append_to_func, args=(".",))
            c3.button("(", on_click=append_to_func, args=("(",))
            c4.button(")", on_click=append_to_func, args=(")",))
            c5.button("y", on_click=append_to_func, args=("y",))

            c1, c2, c3 = st.columns(3)
            c1.button("xʸ (أس)", on_click=append_to_func, args=("**",))
            c2.button("ln( )", on_click=append_to_func, args=("log(",))
            c3.button("e", on_click=append_to_func, args=("e",))

        angle_mode = st.radio(
            "نظام الزوايا:", 
            ["راديان (Rad)", "درجات (Deg)"], 
            horizontal=True
        )

        if "Root" in app_mode:
            method = st.selectbox(
                "طريقة الحل:", 
                ["نيوتن-رافسون (Newton-Raphson)", "التنصيف (Bisection)", "الوضع الخاطئ (False Position)", "القاطع (Secant)"]
            )
            if method in ["التنصيف (Bisection)", "الوضع الخاطئ (False Position)"]:
                col1, col2 = st.columns(2)
                with col1: 
                    a_str = st.text_input("الفترة من (a):", value="1")
                with col2: 
                    b_str = st.text_input("إلى (b):", value="2")
            elif "Newton" in method:
                a_str = st.text_input("نقطة التخمين الابتدائية (x0):", value="1.5")
                b_str = "0"
            elif "Secant" in method:
                col1, col2 = st.columns(2)
                with col1: 
                    a_str = st.text_input("التخمين الأول (x0):", value="1")
                with col2: 
                    b_str = st.text_input("التخمين الثاني (x1):", value="2")
            
            tol_str = st.text_input("نسبة الخطأ المقبولة (Tolerance):", value="1e-6")
            
        elif "Differential" in app_mode:
            method = st.selectbox(
                "طريقة الحل:", 
                ["رينج-كوتا الرابعة (RK4)", "رينج-كوتا الثانية (RK2 - Heun)", "طريقة أويلر (Euler)"]
            )
            col1, col2 = st.columns(2)
            with col1: 
                x0_str = st.text_input("القيمة الابتدائية (x0):", value="0")
            with col2: 
                y0_str = st.text_input("القيمة الابتدائية (y0):", value="1")
            
            xend_str = st.text_input("قيمة x المطلوب حساب y عندها (x_end):", value="0.2")
            input_type = st.radio("طريقة تحديد الخطوة:", ["لدي حجم الخطوة (h)", "لدي عدد الخطوات (n)"], horizontal=True)
            val = st.number_input("أدخل القيمة (h أو n):", value=0.1 if "h" in input_type else 10.0, min_value=0.0001, format="%.4f")
            
        elif "Differentiation" in app_mode:
            method = st.selectbox(
                "طريقة التفاضل:", 
                ["الفروق المركزية (Central - الأدق)", "الفروق الأمامية (Forward)", "الفروق الخلفية (Backward)"]
            )
            col1, col2 = st.columns(2)
            with col1: 
                x0_str = st.text_input("احسب المشتقة عند x =", value="2")
            with col2: 
                h_str = st.text_input("حجم الخطوة (h):", value="0.01")
            
        elif "Integration" in app_mode:
            col1, col2 = st.columns(2)
            with col1: 
                a_str = st.text_input("الحد الأدنى (a):", value="0")
            with col2: 
                b_str = st.text_input("الحد الأقصى (b):", value="2")
            
            input_type = st.radio("طريقة الإدخال:", ["عدد القطاعات (n)", "حجم الخطوة (h)"], horizontal=True)
            val = st.number_input("أدخل القيمة (n أو h):", value=6.0, min_value=0.0001)

    st.markdown("<br>", unsafe_allow_html=True)
    calc_btn = st.button("🚀 احسب وارسم النتائج", type="primary", use_container_width=True)

# ==========================================
# === 5. العمود الأيمن: شاشة النتائج والرسم ===
# ==========================================
with col_display:
    if calc_btn:
        
        # =========================================================================
        # 1. قسم الاستيفاء وتوفيق المنحنيات (Interpolation)
        # =========================================================================
        if "Interpolation" in app_mode:
            try:
                x_vals = edited_pts["X"].values.astype(float)
                y_vals = edited_pts["Y"].values.astype(float)
            except Exception:
                st.error("❌ تأكد من إدخال أرقام صحيحة في جدول X و Y.")
                st.stop()
                
            if len(set(x_vals)) != len(x_vals):
                st.error("❌ قيم X يجب أن تكون فريدة (لا يتكرر نفس الرقم في عمود X).")
                st.stop()
                
            x_sym = sp.Symbol('x')
            n_pts = len(x_vals)
            poly = 0
            
            if "Lagrange" in method:
                st.markdown("### 📚 القانون الرياضي (Lagrange Interpolation):")
                st.latex(r"P(x) = \sum_{i=0}^{n} y_i \prod_{j \neq i} \frac{x - x_j}{x_i - x_j}")
                
                terms_str = []
                for i in range(n_pts):
                    term = y_vals[i]
                    for j in range(n_pts):
                        if i != j:
                            term *= (x_sym - x_vals[j]) / (x_vals[i] - x_vals[j])
                    poly += term
                    terms_str.append(f"L_{i}(x)\\cdot({y_vals[i]})")
                    
                if show_tutorial:
                    st.markdown(f"<div class='result-card tutorial-card'><b>💡 خطوات لاجرانج:</b> يتم تكوين {n_pts} حدود، كل حد يساوي صفر عند باقي النقاط ما عدا النقطة الخاصة به، ثم نجمعهم.</div>", unsafe_allow_html=True)
            
            else: # الفروق المقسمة لنيوتن
                st.markdown("### 📚 القانون الرياضي (Newton's Divided Differences):")
                st.latex(r"P(x) = f[x_0] + f[x_0, x_1](x-x_0) + f[x_0, x_1, x_2](x-x_0)(x-x_1) + \dots")
                
                coef = np.zeros([n_pts, n_pts])
                coef[:, 0] = y_vals
                for j in range(1, n_pts):
                    for i in range(n_pts - j):
                        coef[i][j] = (coef[i+1][j-1] - coef[i][j-1]) / (x_vals[i+j] - x_vals[i])
                
                poly = coef[0, 0]
                for j in range(1, n_pts):
                    term = coef[0, j]
                    for i in range(j):
                        term *= (x_sym - x_vals[i])
                    poly += term
                
                if show_tutorial:
                    dd_cols = [f"الفرق {i}" for i in range(n_pts)]
                    st.markdown("#### 📊 جدول الفروق المقسمة:")
                    st.dataframe(pd.DataFrame(coef, columns=dd_cols).style.format(precision=dp), use_container_width=True)

            poly_simplified = sp.expand(poly)
            p_func = sp.lambdify(x_sym, poly_simplified, "numpy")
            
            st.markdown("### 📍 كثيرة الحدود المستنتجة $P(x)$:")
            st.success(f"**P(x) =** `{poly_simplified}`")
            
            # حساب قيمة عند نقطة محددة إذا طلب المستخدم
            target_val = None
            if target_x_str.strip():
                try:
                    tx = safe_float(target_x_str)
                    ty = float(p_func(tx))
                    target_val = (tx, ty)
                    st.markdown(f"<div class='result-card exact-card'><div class='card-title'>🎯 قيمة الدالة المستوفاة عند X = {tx}</div><div class='card-value exact-value'>P({tx}) = {ty:.{dp}f}</div></div>", unsafe_allow_html=True)
                except Exception:
                    st.warning("⚠️ لم نتمكن من حساب النقطة المستهدفة، تأكد من كتابتها كرقم صحيح.")

            # الرسم البياني للاستيفاء
            x_min_plot = min( list(x_vals) + ([target_val[0]] if target_val else []) ) - 1
            x_max_plot = max( list(x_vals) + ([target_val[0]] if target_val else []) ) + 1
            x_curve = np.linspace(x_min_plot, x_max_plot, 400)
            y_curve = p_func(x_curve)
            if isinstance(y_curve, (int, float)):
                y_curve = np.full_like(x_curve, y_curve)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_curve, y=y_curve, mode='lines', name='منحنى الاستيفاء P(x)', line=dict(color='#2d82ff', width=3)))
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='النقاط الأساسية', marker=dict(color='#ff4b4b', size=12)))
            if target_val:
                fig.add_trace(go.Scatter(x=[target_val[0]], y=[target_val[1]], mode='markers', name=f'النقطة المستهدفة ({target_val[0]})', marker=dict(color='#28a745', size=14, symbol='star')))
            fig.update_layout(title="التمثيل البياني للاستيفاء", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            st.session_state.history.append(f"📉 **استيفاء ({n_pts} نقاط):**\n`P(x) = {poly_simplified}`")

        # =========================================================================
        # 2. قسم أنظمة المعادلات الخطية (Linear Systems)
        # =========================================================================
        elif "Linear" in app_mode:
            try:
                A_input = edited_df.iloc[:, :-1].values.astype(float)
                b_input = edited_df.iloc[:, -1].values.astype(float)
                n = len(b_input)
                if "Elimination" not in method:
                    tol_val = safe_float(tol_str)
            except Exception as e:
                st.error(f"❌ تأكد من صحة الأرقام المدخلة في المصفوفة أو نسبة الخطأ. ({e})")
                st.stop()
                
            if "Elimination" in method:
                st.markdown("### 📚 طريقة الحذف لجاوس (Gaussian Elimination with Partial Pivoting)")
                Ab = np.column_stack((A_input.copy(), b_input.copy()))
                
                for i in range(n):
                    max_row = np.argmax(np.abs(Ab[i:n, i])) + i
                    Ab[[i, max_row]] = Ab[[max_row, i]]
                    
                    if abs(Ab[i, i]) < 1e-15:
                        st.error("❌ المصفوفة شاذة (Singular Matrix) ولا يوجد للنظام حل وحيد.")
                        st.stop()
                        
                    for j in range(i+1, n):
                        factor = Ab[j, i] / Ab[i, i]
                        Ab[j] = Ab[j] - factor * Ab[i]
                        
                x_res = np.zeros(n)
                for i in range(n-1, -1, -1):
                    x_res[i] = (Ab[i, -1] - np.sum(Ab[i, i+1:n] * x_res[i+1:n])) / Ab[i, i]
                    
                if show_tutorial:
                    st.markdown("#### 📐 المصفوفة المثلثية العليا (Upper Triangular Matrix) بعد الحذف:")
                    st.dataframe(pd.DataFrame(Ab, columns=cols).style.format(precision=dp), use_container_width=True)

                st.markdown("### 📍 قيم المتغيرات النهائية:")
                res_df = pd.DataFrame({
                    "المتغير": [f"x{i+1}" for i in range(n)], 
                    "القيمة النهائية": [f"{x_res[i]:.{dp}f}" for i in range(n)]
                })
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                st.session_state.history.append(f"🧮 **حذف جاوس:** تم حل {n} معادلات بنجاح.")
                
            else: # جاكوبي وجاوس-سيدل مع الترتيب الأوتوماتيكي الذكي
                indices = []
                used_rows = set()
                for i in range(n):
                    max_row, max_val = -1, -1
                    for r in range(n):
                        if r not in used_rows and abs(A_input[r, i]) > max_val:
                            max_val = abs(A_input[r, i])
                            max_row = r
                    indices.append(max_row)
                    used_rows.add(max_row)

                A = A_input[indices]
                b = b_input[indices]
                
                if indices != list(range(n)): 
                    st.success("✨ تم إعادة ترتيب المعادلات أوتوماتيكياً لتصبح مسيطرة قطرياً (Diagonally Dominant) لضمان تقارب الحل!")
                    with st.expander("👀 عرض المصفوفة بعد الترتيب الأوتوماتيكي", expanded=False):
                        st.dataframe(pd.DataFrame(np.column_stack((A, b)), columns=cols), use_container_width=True)

                if np.any(np.abs(np.diag(A)) < 1e-15): 
                    st.error("❌ القطر الرئيسي يحتوي على صفر حتى بعد الترتيب. لا يمكن القسمة على صفر.")
                    st.stop()

                # فحص السيطرة القطرية
                is_dd = all(abs(A[i, i]) >= (np.sum(np.abs(A[i])) - abs(A[i, i])) for i in range(n))
                if not is_dd:
                    st.warning("⚠️ تنبيه: المصفوفة ليست مسيطرة قطرياً بالكامل؛ قد تتباعد الأرقام (Diverge) ولكن سنحاول الحل.")

                st.markdown("### 📚 القانون الرياضي المستخدم:")
                if "Jacobi" in method: 
                    st.latex(r"x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j \neq i} a_{ij} x_j^{(k)} \right)")
                else: 
                    st.latex(r"x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j < i} a_{ij} x_j^{(k+1)} - \sum_{j > i} a_{ij} x_j^{(k)} \right)")

                x_arr = np.zeros(n)
                steps_data = []
                iterations = 0
                final_error = 0
                max_iter = 500
                
                for it in range(max_iter):
                    x_new = np.zeros(n)
                    for i in range(n):
                        s = 0
                        for j in range(n):
                            if i != j:
                                if "Jacobi" in method: 
                                    s += A[i, j] * x_arr[j]
                                else: 
                                    s += A[i, j] * (x_new[j] if j < i else x_arr[j])
                        x_new[i] = (b[i] - s) / A[i, i]
                        
                        if show_tutorial and it == 0 and i == 0:
                            msg = f"<b>💡 شرح التعويض (المحاولة الأولى للمتغير x1):</b><br> x1 = ( {b[i]} - ({s:.{dp}f}) ) / {A[i,i]} = <b>{x_new[i]:.{dp}f}</b>"
                            st.markdown(f"<div class='result-card tutorial-card'>{msg}</div>", unsafe_allow_html=True)
                    
                    error = np.max(np.abs(x_new - x_arr))
                    
                    step_dict = {"Iteration": it + 1}
                    for i in range(n): 
                        step_dict[f"x{i+1}"] = f"{x_new[i]:.{dp}f}"
                    step_dict["Error"] = f"{error:.2e}"
                    steps_data.append(step_dict)
                    
                    iterations = it + 1
                    final_error = error
                    x_arr = x_new.copy()
                    
                    if error < tol_val: 
                        break
                    if error > 1e12: 
                        st.error("❌ النظام متباعد (Diverging)! الأرقام تتجه نحو المالانهاية.")
                        break

                st.markdown("### 📍 قيم المتغيرات النهائية:")
                res_df = pd.DataFrame({
                    "المتغير": [f"x{i+1}" for i in range(n)],
                    "القيمة النهائية": [f"{x_arr[i]:.{dp}f}" for i in range(n)]
                })
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                if final_error < tol_val:
                    st.success(f"✅ تم الوصول للحل الدقيق بعد **{iterations} محاولة** | أقصى خطأ: **{final_error:.2e}**")

                st.markdown("### 📝 جدول خطوات الحل (Iterations Table)")
                df_steps = pd.DataFrame(steps_data)
                st.dataframe(df_steps, use_container_width=True, hide_index=True)
                
                csv = df_steps.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل جدول المحاولات كملف إكسيل (CSV)", data=csv, file_name='linear_system_iterations.csv', mime='text/csv', use_container_width=True)
                
                st.session_state.history.append(f"🧮 **{method.split(' ')[0]}:** {n} متغيرات ({iterations} خطوة)")

        # =========================================================================
        # 3. الأقسام المعتمدة على الدوال (الجذور، المعادلات التفاضلية، التفاضل، التكامل)
        # =========================================================================
        else:
            if not func_input.strip():
                st.warning("⚠️ يرجى كتابة الدالة الرياضية أولاً.")
                st.stop()
                
            func_clean = func_input.replace('^', '**').replace('ln', 'log').replace(' ', '')
            x_sym, y_sym = sp.Symbol('x'), sp.Symbol('y')
            custom_dict = {'e': sp.E, 'pi': sp.pi}
            
            if "Deg" in angle_mode:
                custom_dict.update({
                    'sin': lambda arg: sp.sin(arg * sp.pi / 180), 
                    'cos': lambda arg: sp.cos(arg * sp.pi / 180), 
                    'tan': lambda arg: sp.tan(arg * sp.pi / 180)
                })

            try:
                f_expr = sp.sympify(func_clean, locals=custom_dict)
                if "Differential" in app_mode:
                    f = sp.lambdify((x_sym, y_sym), f_expr, "numpy")
                else:
                    f = sp.lambdify(x_sym, f_expr, "numpy")
            except Exception as e:
                st.error(f"❌ خطأ في صيغة الدالة الرياضية. تأكد من كتابة علامة الضرب `*` والأقواس بشكل سليم. ({e})")
                st.stop()

            # ---------------------------------------------------------------------
            # أ. قسم حل المعادلات (Root Finding)
            # ---------------------------------------------------------------------
            if "Root" in app_mode:
                try:
                    a_val = safe_float(a_str)
                    b_val = safe_float(b_str)
                    tol_val = safe_float(tol_str)
                except Exception as e:
                    st.error(f"❌ خطأ في الأرقام المدخلة لنقاط البداية أو نسبة الخطأ. ({e})")
                    st.stop()

                root, iterations, error = None, 0, 0
                steps_data = []

                st.markdown("### 📚 القانون الرياضي المستخدم:")
                if "Bisection" in method:
                    st.latex(r"c = \frac{a + b}{2}")
                elif "False Position" in method:
                    st.latex(r"c = \frac{a \cdot f(b) - b \cdot f(a)}{f(b) - f(a)}")
                elif "Newton" in method:
                    df_expr = sp.diff(f_expr, x_sym)
                    st.latex(r"x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}")
                    st.info(f"📐 **المشتقة الأولى المحسوبة تلقائياً:** `f'(x) = {df_expr}`")
                elif "Secant" in method:
                    st.latex(r"x_{i+1} = x_i - f(x_i) \frac{x_i - x_{i-1}}{f(x_i) - f(x_{i-1})}")

                if method in ["التنصيف (Bisection)", "الوضع الخاطئ (False Position)"]:
                    if a_val >= b_val:
                        st.error("❌ يجب أن تكون النقطة (b) أكبر من النقطة (a).")
                        st.stop()
                    fa, fb = float(f(a_val)), float(f(b_val))
                    if fa * fb > 0:
                        st.error(f"❌ شرط الحل غير متحقق: f({a_val})={fa:.3f} و f({b_val})={fb:.3f} لهما نفس الإشارة! يجب أن تقطع الدالة محور السينات بينهما.")
                        st.stop()
                    
                    a_temp, b_temp = a_val, b_val
                    for i in range(100):
                        fa_t, fb_t = float(f(a_temp)), float(f(b_temp))
                        if "Bisection" in method:
                            c = (a_temp + b_temp) / 2.0
                        else:
                            c = (a_temp * fb_t - b_temp * fa_t) / (fb_t - fa_t)
                            
                        fc = float(f(c))
                        current_err = abs(b_temp - a_temp) / 2.0 if "Bisection" in method else abs(fc)
                        
                        steps_data.append({
                            "Iteration (i)": i + 1,
                            "a": f"{a_temp:.{dp}f}",
                            "b": f"{b_temp:.{dp}f}",
                            "Root (c)": f"{c:.{dp}f}",
                            "f(c)": f"{fc:.{dp}f}",
                            "Error": f"{current_err:.2e}"
                        })
                        
                        if abs(fc) < tol_val or current_err < tol_val:
                            root, iterations, error = c, i + 1, current_err
                            break
                        if fa_t * fc < 0:
                            b_temp = c
                        else:
                            a_temp = c
                    if root is None:
                        root, iterations, error = c, 100, current_err

                elif "Newton" in method:
                    df = sp.lambdify(x_sym, df_expr, "numpy")
                    x_curr = a_val
                    for i in range(100):
                        fx, dfx = float(f(x_curr)), float(df(x_curr))
                        if abs(dfx) < 1e-15:
                            st.error("❌ المشتقة تساوي صفر عند هذه النقطة! طريقة نيوتن تتوقف هنا (قسمة على صفر).")
                            st.stop()
                        
                        x_next = x_curr - (fx / dfx)
                        current_err = abs(x_next - x_curr)
                        
                        if show_tutorial and i == 0:
                            msg = f"<b>💡 تعويض المحاولة الأولى (i=1):</b><br> x₁ = {x_curr} - ( {fx:.{dp}f} / {dfx:.{dp}f} ) = <b>{x_next:.{dp}f}</b>"
                            st.markdown(f"<div class='result-card tutorial-card'>{msg}</div>", unsafe_allow_html=True)

                        steps_data.append({
                            "Iteration (i)": i + 1,
                            "X_i": f"{x_curr:.{dp}f}",
                            "f(X_i)": f"{fx:.{dp}f}",
                            "f'(X_i)": f"{dfx:.{dp}f}",
                            "X_{i+1}": f"{x_next:.{dp}f}",
                            "Error": f"{current_err:.2e}"
                        })
                        
                        if current_err < tol_val:
                            root, iterations, error = x_next, i + 1, current_err
                            break
                        x_curr = x_next
                    if root is None:
                        root, iterations, error = x_curr, 100, current_err

                elif "Secant" in method:
                    x0, x1 = a_val, b_val
                    for i in range(100):
                        f0, f1 = float(f(x0)), float(f(x1))
                        if abs(f1 - f0) < 1e-15:
                            st.error("❌ الفرق بين الدالتين يساوي صفر (قسمة على صفر).")
                            st.stop()
                        
                        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
                        current_err = abs(x2 - x1)
                        
                        steps_data.append({
                            "Iteration (i)": i + 1,
                            "X_{i-1}": f"{x0:.{dp}f}",
                            "X_i": f"{x1:.{dp}f}",
                            "f(X_i)": f"{f1:.{dp}f}",
                            "X_{i+1}": f"{x2:.{dp}f}",
                            "Error": f"{current_err:.2e}"
                        })
                        
                        if current_err < tol_val:
                            root, iterations, error = x2, i + 1, current_err
                            break
                        x0, x1 = x1, x2
                    if root is None:
                        root, iterations, error = x2, 100, current_err

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.markdown(f"<div class='result-card exact-card'><div class='card-title'>📍 قيمة الجذر النهائي (Root)</div><div class='card-value exact-value'>{root:.{dp}f}</div></div>", unsafe_allow_html=True)
                with res_col2:
                    st.markdown(f"<div class='result-card'><div class='card-title'>⚙️ الأداء والدقة</div><div class='card-value' style='font-size:22px;'>الخطأ: {error:.2e}</div><div class='card-subtext'>تم الوصول للحل بعد {iterations} خطوة</div></div>", unsafe_allow_html=True)

                st.markdown("### 📝 جدول خطوات الحل (Iterations Table)")
                df_steps = pd.DataFrame(steps_data)
                st.dataframe(df_steps, use_container_width=True, hide_index=True)
                
                csv = df_steps.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل جدول المحاولات كملف إكسيل (CSV)", data=csv, file_name='root_iterations.csv', mime='text/csv', use_container_width=True)

                st.markdown("### 🎨 الرسم البياني التفاعلي للدالة والجذر")
                x_min, x_max = root - 2.5, root + 2.5
                x_smooth = np.linspace(x_min, x_max, 500)
                y_smooth = f(x_smooth)
                if isinstance(y_smooth, (int, float)):
                    y_smooth = np.full_like(x_smooth, y_smooth)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='f(x)', line=dict(color='#2d82ff', width=3)))
                fig.add_trace(go.Scatter(x=[x_min, x_max], y=[0, 0], mode='lines', name='محور السينات (y=0)', line=dict(color='#ff4b4b', width=2, dash='dash')))
                fig.add_trace(go.Scatter(x=[root], y=[0], mode='markers', name=f'الجذر ({root:.4f})', marker=dict(color='#28a745', size=14, symbol='circle')))
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                st.session_state.history.append(f"🎯 **جذر ({method.split(' ')[0]}):**\n`{func_input}` ⬅️ `{root:.{dp}f}`")

            # ---------------------------------------------------------------------
            # ب. قسم المعادلات التفاضلية (Differential Equations - ODEs)
            # ---------------------------------------------------------------------
            elif "Differential" in app_mode:
                try:
                    x0 = safe_float(x0_str)
                    y0 = safe_float(y0_str)
                    x_end = safe_float(xend_str)
                except Exception as e:
                    st.error(f"❌ خطأ في الأرقام المدخلة (تأكد من كتابة القيم بشكل سليم). التفاصيل: {e}")
                    st.stop()

                if "h" in input_type:
                    h = float(val)
                    n = int(round(abs(x_end - x0) / h))
                else:
                    n = int(val)
                    h = abs(x_end - x0) / n

                if x_end < x0:
                    h = -h

                st.markdown("### 📚 القوانين الرياضية المستخدمة:")
                if "Euler" in method:
                    st.latex(r"y_{i+1} = y_i + h \cdot f(x_i, y_i)")
                elif "RK2" in method:
                    st.latex(r"k_1 = h f(x_i, y_i), \quad k_2 = h f(x_i + h, y_i + k_1), \quad y_{i+1} = y_i + \frac{1}{2}(k_1 + k_2)")
                else: # RK4
                    st.latex(r"\begin{aligned} k_1 &= h f(x_i, y_i) \\ k_2 &= h f\left(x_i + \frac{h}{2}, y_i + \frac{k_1}{2}\right) \\ k_3 &= h f\left(x_i + \frac{h}{2}, y_i + \frac{k_2}{2}\right) \\ k_4 &= h f(x_i + h, y_i + k_3) \\ y_{i+1} &= y_i + \frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4) \end{aligned}")

                x_vals, y_vals = [x0], [y0]
                steps_data = []

                for i in range(n):
                    xi, yi = x_vals[-1], y_vals[-1]
                    try:
                        if "Euler" in method:
                            slope = float(f(xi, yi))
                            y_next = yi + h * slope
                            steps_data.append({
                                "Step": i + 1,
                                "x_i": f"{xi:.{dp}f}",
                                "y_i": f"{yi:.{dp}f}",
                                "f(x_i, y_i)": f"{slope:.{dp}f}",
                                "y_{i+1}": f"{y_next:.{dp}f}"
                            })
                        elif "RK2" in method:
                            k1 = h * float(f(xi, yi))
                            k2 = h * float(f(xi + h, yi + k1))
                            y_next = yi + 0.5 * (k1 + k2)
                            steps_data.append({
                                "Step": i + 1,
                                "x_i": f"{xi:.{dp}f}",
                                "y_i": f"{yi:.{dp}f}",
                                "k1": f"{k1:.{dp}f}",
                                "k2": f"{k2:.{dp}f}",
                                "y_{i+1}": f"{y_next:.{dp}f}"
                            })
                        else: # RK4
                            k1 = h * float(f(xi, yi))
                            k2 = h * float(f(xi + h/2.0, yi + k1/2.0))
                            k3 = h * float(f(xi + h/2.0, yi + k2/2.0))
                            k4 = h * float(f(xi + h, yi + k3))
                            y_next = yi + (k1 + 2.0*k2 + 2.0*k3 + k4) / 6.0
                            
                            if show_tutorial and i == 0:
                                msg = f"<b>💡 حسابات الخطوة الأولى (RK4):</b><br> k₁ = {k1:.{dp}f} | k₂ = {k2:.{dp}f} | k₃ = {k3:.{dp}f} | k₄ = {k4:.{dp}f}<br> y₁ = {yi} + (k₁ + 2k₂ + 2k₃ + k₄)/6 = <b>{y_next:.{dp}f}</b>"
                                st.markdown(f"<div class='result-card tutorial-card'>{msg}</div>", unsafe_allow_html=True)

                            steps_data.append({
                                "Step": i + 1,
                                "x_i": f"{xi:.{dp}f}",
                                "y_i": f"{yi:.{dp}f}",
                                "k1": f"{k1:.{dp}f}",
                                "k2": f"{k2:.{dp}f}",
                                "k3": f"{k3:.{dp}f}",
                                "k4": f"{k4:.{dp}f}",
                                "y_{i+1} ( عند x=" + f"{xi+h:.3f} )": f"{y_next:.{dp}f}"
                            })
                    except Exception as e:
                        st.error(f"❌ خطأ رياضي أثناء التعويض: {e}")
                        st.stop()
                        
                    x_vals.append(round(xi + h, 10))
                    y_vals.append(y_next)

                final_y = y_vals[-1]
                st.markdown(f"<div class='result-card exact-card'><div class='card-title'>📍 قيمة y النهائية عند x = {x_vals[-1]}</div><div class='card-value exact-value'>y({x_vals[-1]}) = {final_y:.{dp}f}</div><div class='card-subtext'>تم الحساب على {n} خطوة بحجم خطوة h = {h}</div></div>", unsafe_allow_html=True)

                st.markdown("### 📝 جدول خطوات الحل التفصيلي")
                df_steps = pd.DataFrame(steps_data)
                st.dataframe(df_steps, use_container_width=True, hide_index=True)
                
                csv = df_steps.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل جدول الخطوات كملف إكسيل (CSV)", data=csv, file_name='ode_steps.csv', mime='text/csv', use_container_width=True)

                st.markdown("### 🎨 الرسم البياني لمسار حل المعادلة التفاضلية")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name='مسار الحل التقريبي y(x)', line=dict(color='#2d82ff', width=3), marker=dict(size=9, color='#28a745')))
                fig.update_layout(xaxis_title="X", yaxis_title="Y", hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                st.session_state.history.append(f"🔬 **تفاضلية ({method.split(' ')[0]}):**\n`y({x_vals[-1]}) = {final_y:.{dp}f}`")

            # ---------------------------------------------------------------------
            # ج. قسم التفاضل العددي (Numerical Differentiation)
            # ---------------------------------------------------------------------
            elif "Differentiation" in app_mode:
                try:
                    x0 = safe_float(x0_str)
                    h = safe_float(h_str)
                except Exception as e:
                    st.error(f"❌ تأكد من كتابة قيمة x وحجم الخطوة h بشكل صحيح. ({e})")
                    st.stop()

                # القيمة الدقيقة التحليلية للمشتقة للمقارنة
                df_expr = sp.diff(f_expr, x_sym)
                df_exact_func = sp.lambdify(x_sym, df_expr, "numpy")
                exact_deriv = float(df_exact_func(x0))

                # حساب الفروق الثلاثة
                f_x0 = float(f(x0))
                f_plus = float(f(x0 + h))
                f_minus = float(f(x0 - h))

                forward_val = (f_plus - f_x0) / h
                backward_val = (f_x0 - f_minus) / h
                central_val = (f_plus - f_minus) / (2.0 * h)

                st.markdown("### 📚 القوانين الرياضية للفروق (Finite Differences):")
                st.latex(r"\text{Forward: } f'(x) \approx \frac{f(x+h) - f(x)}{h} \quad | \quad \text{Backward: } f'(x) \approx \frac{f(x) - f(x-h)}{h}")
                st.latex(r"\text{Central (الأدق): } f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}")

                if "Forward" in method:
                    chosen_val = forward_val
                    tut_str = f"( f({x0+h}) - f({x0}) ) / {h} = ({f_plus:.{dp}f} - {f_x0:.{dp}f}) / {h}"
                elif "Backward" in method:
                    chosen_val = backward_val
                    tut_str = f"( f({x0}) - f({x0-h}) ) / {h} = ({f_x0:.{dp}f} - {f_minus:.{dp}f}) / {h}"
                else:
                    chosen_val = central_val
                    tut_str = f"( f({x0+h}) - f({x0-h}) ) / (2 × {h}) = ({f_plus:.{dp}f} - {f_minus:.{dp}f}) / {2*h}"

                if show_tutorial:
                    st.markdown(f"<div class='result-card tutorial-card'><b>💡 خطوة التعويض المباشر:</b><br> f'({x0}) ≈ {tut_str} = <b>{chosen_val:.{dp}f}</b></div>", unsafe_allow_html=True)

                c_res1, c_res2 = st.columns(2)
                with c_res1:
                    st.markdown(f"<div class='result-card'><div class='card-title'>📐 المشتقة العددية ({method.split('(')[0]})</div><div class='card-value'>{chosen_val:.{dp}f}</div><div class='card-subtext'>الخطأ المطلق: {abs(exact_deriv - chosen_val):.2e}</div></div>", unsafe_allow_html=True)
                with c_res2:
                    st.markdown(f"<div class='result-card exact-card'><div class='card-title'>🎯 المشتقة التحليلية الدقيقة (Exact)</div><div class='card-value exact-value'>{exact_deriv:.{dp}f}</div><div class='card-subtext'>f'(x) = {df_expr}</div></div>", unsafe_allow_html=True)

                st.markdown("### ⚖️ جدول مقارنة جميع طرق التفاضل العددي:")
                diff_df = pd.DataFrame([
                    {"الطريقة": "الفروق الأمامية (Forward)", "القيمة التقريبية": f"{forward_val:.{dp}f}", "مقدار الخطأ": f"{abs(exact_deriv - forward_val):.2e}"},
                    {"الطريقة": "الفروق الخلفية (Backward)", "القيمة التقريبية": f"{backward_val:.{dp}f}", "مقدار الخطأ": f"{abs(exact_deriv - backward_val):.2e}"},
                    {"الطريقة": "الفروق المركزية (Central)", "القيمة التقريبية": f"{central_val:.{dp}f}", "مقدار الخطأ": f"{abs(exact_deriv - central_val):.2e}"}
                ])
                st.dataframe(diff_df, use_container_width=True, hide_index=True)

                # رسم الدالة والمماس عند النقطة
                st.markdown("### 🎨 الرسم البياني للدالة وخط المماس (Tangent Line)")
                x_range = np.linspace(x0 - 2, x0 + 2, 300)
                y_range = f(x_range)
                if isinstance(y_range, (int, float)):
                    y_range = np.full_like(x_range, y_range)
                y_tangent = f_x0 + chosen_val * (x_range - x0)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_range, y=y_range, mode='lines', name='الدالة f(x)', line=dict(color='#2d82ff', width=3)))
                fig.add_trace(go.Scatter(x=x_range, y=y_tangent, mode='lines', name='المماس التقريبي', line=dict(color='#ff4b4b', width=2, dash='dash')))
                fig.add_trace(go.Scatter(x=[x0], y=[f_x0], mode='markers', name=f'نقطة التماس x={x0}', marker=dict(color='#28a745', size=12)))
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                st.session_state.history.append(f"📐 **تفاضل عند x={x0}:**\nالنتيجة: `{chosen_val:.{dp}f}`")

            # ---------------------------------------------------------------------
            # د. قسم التكامل العددي (Numerical Integration)
            # ---------------------------------------------------------------------
            elif "Integration" in app_mode:
                try:
                    a_val = safe_float(a_str)
                    b_val = safe_float(b_str)
                except Exception as e:
                    st.error(f"❌ تأكد من كتابة حدود التكامل a و b بشكل صحيح. ({e})")
                    st.stop()

                if a_val >= b_val:
                    st.error("❌ الحد الأقصى (b) يجب أن يكون أكبر من الحد الأدنى (a).")
                    st.stop()

                st.markdown("### 📚 القوانين الرياضية للتكامل العددي:")
                st.latex(r"\text{Trapezoidal: } \int_{a}^{b} f(x) dx \approx \frac{h}{2} \left[ y_0 + 2 \sum_{i=1}^{n-1} y_i + y_n \right]")
                st.latex(r"\text{Simpson's 1/3: } \int_{a}^{b} f(x) dx \approx \frac{h}{3} \left[ y_0 + 4 \sum_{i \text{ odd}} y_i + 2 \sum_{i \text{ even}} y_i + y_n \right]")
                st.latex(r"\text{Simpson's 3/8: } \int_{a}^{b} f(x) dx \approx \frac{3h}{8} \left[ y_0 + 3 \sum_{i \neq 3k} y_i + 2 \sum_{i = 3k} y_i + y_n \right]")

                exact_val, _ = quad(lambda t: float(f(t)), a_val, b_val)

                if "h" in input_type:
                    h = float(val)
                    n = int(round((b_val - a_val) / h))
                else:
                    n = int(val)
                    h = (b_val - a_val) / n

                x_vals = np.linspace(a_val, b_val, n + 1)
                y_vals = [float(f(xv)) for xv in x_vals]

                # حساب الطرق الثلاثة
                trap_val = (h / 2.0) * (y_vals[0] + 2.0 * np.sum(y_vals[1:-1]) + y_vals[-1])
                
                simp13_val = None
                if n % 2 == 0:
                    simp13_val = (h / 3.0) * (y_vals[0] + 4.0 * np.sum(y_vals[1:-1:2]) + 2.0 * np.sum(y_vals[2:-2:2]) + y_vals[-1])
                
                simp38_val = None
                if n % 3 == 0:
                    integral = y_vals[0] + y_vals[-1]
                    for i in range(1, n):
                        integral += 2.0 * y_vals[i] if i % 3 == 0 else 3.0 * y_vals[i]
                    simp38_val = (3.0 * h / 8.0) * integral

                st.markdown(f"<div class='result-card exact-card'><div class='card-title'>🎯 القيمة الدقيقة التحليلية (Exact Integration)</div><div class='card-value exact-value'>{exact_val:.{dp}f}</div><div class='card-subtext'>عدد القطاعات n = {n} | طول الخطوة h = {h:.{dp}f}</div></div>", unsafe_allow_html=True)

                if show_tutorial:
                    pts_df = pd.DataFrame({"i": range(n+1), "x_i": x_vals, "y_i = f(x_i)": y_vals})
                    with st.expander("👀 عرض جدول نقاط التعويض (x_i , y_i)", expanded=True):
                        st.dataframe(pts_df.style.format({"x_i": f"{{:.{dp}f}}", "y_i = f(x_i)": f"{{:.{dp}f}}"}), use_container_width=True, hide_index=True)

                st.markdown("### ⚖️ مقارنة نتائج طرق التكامل العددي:")
                df_data = []
                methods_list = [
                    ("شبه المنحرف (Trapezoidal)", trap_val),
                    ("سيمبسون 1/3 (Simpson's 1/3)", simp13_val),
                    ("سيمبسون 3/8 (Simpson's 3/8)", simp38_val)
                ]
                for m_name, m_val in methods_list:
                    if m_val is not None:
                        err = abs(exact_val - m_val)
                        df_data.append({"الطريقة": m_name, "النتيجة التقريبية": f"{m_val:.{dp}f}", "الخطأ المطلق": f"{err:.2e}"})
                    else:
                        reason = "يتطلب عدد قطاعات n زوجي" if "1/3" in m_name else "يتطلب n من مضاعفات الرقم 3"
                        df_data.append({"الطريقة": m_name, "النتيجة التقريبية": f"❌ ({reason})", "الخطأ المطلق": "-"})
                
                df_int = pd.DataFrame(df_data)
                st.dataframe(df_int, use_container_width=True, hide_index=True)

                csv = df_int.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل جدول مقارنة التكامل كملف إكسيل (CSV)", data=csv, file_name='integration_comparison.csv', mime='text/csv', use_container_width=True)

                st.markdown("### 🎨 الرسم البياني التفاعلي للمساحة تحت المنحنى")
                x_smooth = np.linspace(a_val, b_val, 500)
                y_smooth = f(x_smooth)
                if isinstance(y_smooth, (int, float)):
                    y_smooth = np.full_like(x_smooth, y_smooth)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='f(x)', line=dict(color='#2d82ff', width=3)))
                fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, fill='tozeroy', fillcolor='rgba(45, 130, 255, 0.2)', mode='none', name='المساحة المحسوبة'))
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name='نقاط التقسيم', marker=dict(color='#ff4b4b', size=8)))
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                st.session_state.history.append(f"📈 **تكامل:** `{func_input}`\nالنتيجة: `{exact_val:.{dp}f}`")

    else:
        st.info(f"👋 أهلاً بك يا باشمهندس! أنت الآن في قسم **{app_mode}**. قم بضبط المدخلات في اللوحة اليسرى ثم اضغط على زر **🚀 احسب وارسم النتائج**.")
