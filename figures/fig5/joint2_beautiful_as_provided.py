"""The author's working script for the joint-attack figure, as provided.

This is the most recent script the author has for Fig. 5. It is NOT the script
that produced the submitted `P_joint.pdf`, and it does not regenerate it: it uses
m = 80 and T_coh = 1 s (the published figure uses m = 30 and T_coh = 20 s), plots
log2 of the probabilities rather than the probabilities, and models the SWAP
survival as P_SWAP = exp(-t/T_coh) instead of the published
(1 + exp(-t/T_coh))/2, which tends to 1/2 rather than to 0. The closed form for
P_LWE is the same one the paper states.

It is kept here as the author's own artifact. `plot_fig5_joint_probability.py`
in this directory is the reimplementation that does reproduce the published
figure's annotations and generates `source_data/SourceData_Fig5.csv`.

Run as provided it calls plt.show() and writes log2Pr_joint_beautiful.pdf/.png
into the current working directory.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf

# 设置现代科学绘图样式（不依赖seaborn）
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'axes.linewidth': 1.2,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12,
    'legend.frameon': True,
    'legend.fancybox': True,
    'legend.shadow': True,
    'figure.figsize': (12, 7),
    'lines.linewidth': 2.5,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.8,
    'axes.axisbelow': True,
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.grid': True
})

# 精确计算 log2 Pr
def log2_Pr_exact(m, a, b, t, s, b1_norm, di=None):
    if di is None:
        di = np.ones(m)
    gamma = 2 * a / (np.log2(t) + b)
    pi = np.pi
    lambda_ = b1_norm * np.sqrt(pi) / (2 * s)
    i_vals = np.arange(1, m + 1)
    z_i = di * lambda_ * 2 ** (-gamma * (i_vals - 1))
    return np.sum(np.log2(erf(z_i)))

# swap pr
def P_swap(t, T_coh):
    return np.log2(np.exp(-t/T_coh))

# 设置 di 全为 2
def get_di_vector(m, value=2):
    return np.full(m, value)

# 数据计算
t_vals = np.arange(10, 100, 5)
log2_classical_list = []
log2_swap_list = []
log2_joint_list = []
m = 80
T_coh = 1
di_vec = get_di_vector(m, value=2)

for t in t_vals:
    log2_Pclassical = log2_Pr_exact(m, a=0.3, b=2.7, t=t, s=2, b1_norm=10, di=di_vec)
    log2_Pswap = P_swap(t, T_coh)
    log2_Pjoint = log2_Pclassical + log2_Pswap
    log2_classical_list.append(log2_Pclassical)
    log2_swap_list.append(log2_Pswap)
    log2_joint_list.append(log2_Pjoint)

# 创建美化的图表
fig, ax = plt.subplots(1, 1, figsize=(13, 8))

# 定义专业的颜色方案
colors = {
    'classical': '#2E8B57',  # Sea Green
    'swap': '#DC143C',       # Crimson  
    'joint': '#1E90FF'       # Dodger Blue
}

# 绘制曲线，使用不同的线型和标记
line1 = ax.plot(t_vals, log2_classical_list, 
                color=colors['classical'], 
                linestyle='-', 
                linewidth=3,
                marker='o', 
                markersize=6,
                markerfacecolor='white',
                markeredgecolor=colors['classical'],
                markeredgewidth=2,
                label=r'$\log_2 P_{\mathrm{LWE}}$',
                alpha=0.9)

line2 = ax.plot(t_vals, log2_swap_list, 
                color=colors['swap'],
                linestyle='--', 
                linewidth=3,
                marker='s', 
                markersize=6,
                markerfacecolor='white',
                markeredgecolor=colors['swap'],
                markeredgewidth=2,
                label=r'$\log_2 P_{\mathrm{SWAP}}$',
                alpha=0.9)

line3 = ax.plot(t_vals, log2_joint_list, 
                color=colors['joint'],
                linestyle='-.', 
                linewidth=3.5,
                marker='^', 
                markersize=7,
                markerfacecolor=colors['joint'],
                markeredgecolor='white',
                markeredgewidth=1,
                label=r'$\log_2 P_{\mathrm{joint}}$',
                alpha=0.95)

# 设置坐标轴标签和标题
ax.set_xlabel('')  # xlabel 由下方 ax.text 手动放置，与公式框同行
ax.set_ylabel(r'$\log_2 \mathrm{Pr}$', fontsize=16, fontweight='bold')
ax.set_title('Quantum Teleportation Security Analysis:\n' + 
             r'$P_{\mathrm{joint}} = P_{\mathrm{LWE}} \times P_{\mathrm{SWAP}}$', 
             fontsize=18, fontweight='bold', pad=20)

# 设置网格
ax.grid(True, linestyle='-', alpha=0.3, linewidth=0.8, color='gray')
ax.set_axisbelow(True)

# 美化坐标轴
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# 设置刻度
ax.tick_params(axis='both', which='major', labelsize=12, 
               length=6, width=1.2, direction='in')

# 添加图例，移到图外右侧避免遮挡曲线
legend = ax.legend(loc='upper left',
                  bbox_to_anchor=(1.02, 1),
                  borderaxespad=0,
                  frameon=True,
                  fancybox=True,
                  shadow=True,
                  framealpha=0.95,
                  fontsize=14)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_edgecolor('gray')
legend.get_frame().set_linewidth(1.2)

# 添加参数信息文本框（放在图外右侧，legend 下面）
param_text = f'Parameters:\n$m = {m}$, $T_{{coh}} = {T_coh}$ s\n$a = 0.3$, $b = 2.7$, $s = 2$'
ax.text(1.02, 0.55, param_text,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment='top',
        horizontalalignment='left',
        bbox=dict(boxstyle='round,pad=0.5', 
                 facecolor='lightblue', 
                 alpha=0.8,
                 edgecolor='navy',
                 linewidth=1))

# xlabel 与数学公式框放在同一行（axes 坐标系，y=-0.10 约与 x轴刻度标签同行偏下）
ax.text(0.02, -0.10, r'Time $t$ (seconds)',
        transform=ax.transAxes,
        fontsize=16, fontweight='bold',
        verticalalignment='top',
        horizontalalignment='left')

math_text = r'$\log_2 P_{\mathrm{joint}} = \log_2 P_{\mathrm{LWE}} + \log_2 P_{\mathrm{SWAP}}$'
ax.text(0.98, -0.10, math_text,
        transform=ax.transAxes,
        fontsize=13,
        horizontalalignment='right',
        verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.4',
                 facecolor='lightyellow',
                 alpha=0.9,
                 edgecolor='orange',
                 linewidth=1))

# 调整布局，留出底部空间放同行标注
plt.tight_layout(rect=[0, 0.13, 0.78, 1])

# 保存高质量图片
plt.savefig("log2Pr_joint_beautiful.pdf", 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none')

plt.savefig("log2Pr_joint_beautiful.png", 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none')

plt.show()

# 打印统计信息
print("=== 数据统计 ===")
print(f"时间范围: {t_vals[0]} - {t_vals[-1]} 秒")
print(f"log₂(P_LWE) 范围: {min(log2_classical_list):.2f} - {max(log2_classical_list):.2f}")
print(f"log₂(P_SWAP) 范围: {min(log2_swap_list):.2f} - {max(log2_swap_list):.2f}")
print(f"log₂(P_joint) 范围: {min(log2_joint_list):.2f} - {max(log2_joint_list):.2f}")

# 找到联合攻击概率的峰值
max_joint_idx = np.argmax(log2_joint_list)
print(f"联合攻击概率峰值: t = {t_vals[max_joint_idx]} 秒, log₂(P_joint) = {log2_joint_list[max_joint_idx]:.2f}")