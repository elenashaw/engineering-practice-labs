#plot_results.py - 这个程序读取Floyd算法性能测试的CSV结果文件，并生成多个图表来比较不同测试场景下的性能表现。它包括线图、柱状图、热力图和散点图，以全面展示不同变体在不同链表配置下的性能差异。
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# 1. 加载并规范数据
df = pd.read_csv('floyd_raw_data.csv')
df['TotalSize'] = df['TotalSize'].astype(int)
df['StepK'] = df['StepK'].astype(int)

# 定义环场景顺序
scenario_order = ["NoCycle", "Small(1%)", "Mod(30%)", "Mod(60%)", "Large(90%)"]
df['CycleType'] = pd.Categorical(df['CycleType'], categories=scenario_order, ordered=True)

# 2. 设置绘图风格
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 3. 创建画布：5行(场景) x 2列(K轴)
# 增大高度至 35，确保 10 张子图之间有充足间隙
fig, axes = plt.subplots(5, 2, figsize=(16, 35))
plt.subplots_adjust(hspace=0.6, wspace=0.25, top=0.94)

fig.suptitle('Floyd 算法性能全维度对比：总执行时间 (ms)', fontsize=26, y=0.98)

for i, scenario in enumerate(scenario_order):
    scenario_data = df[df['CycleType'] == scenario]
    
    # --- 左列：线性步长 (k = 1 to 20) ---
    ax_l = axes[i, 0]
    sns.lineplot(data=scenario_data[scenario_data['StepK'] <= 20], 
                 x='StepK', y='AvgTime', hue='TotalSize', 
                 marker='o', palette='turbo', ax=ax_l, legend=(i==0))
    
    ax_l.set_title(f'【{scenario}】线性步长区 k=[1, 20]', fontsize=16, pad=15)
    ax_l.set_xticks(range(1, 21, 2)) # 隔位显示整数刻度
    ax_l.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax_l.set_xlabel('步长 k')
    ax_l.set_ylabel('平均耗时 (ms)')

    # --- 右列：指数步长 (k = 2 to 256) ---
    ax_r = axes[i, 1]
    exp_ks = [2, 4, 8, 16, 32, 64, 128, 256]
    sns.lineplot(data=scenario_data[scenario_data['StepK'].isin(exp_ks)], 
                 x='StepK', y='AvgTime', hue='TotalSize', 
                 marker='D', palette='turbo', ax=ax_r, legend=False)
    
    ax_r.set_title(f'【{scenario}】指数步长区 k=[2, 256]', fontsize=16, pad=15)
    ax_r.set_xscale('log', base=2)
    ax_r.set_xticks(exp_ks)
    ax_r.get_xaxis().set_major_formatter(ticker.ScalarFormatter()) # 强制显示原始整数
    ax_r.set_xlabel('步长 k (对数轴)')
    ax_r.set_ylabel('平均耗时 (ms)')

    # 仅在顶部子图显示图例，避免重复挤占
    if i == 0:
        ax_l.legend(title='链表长度 (N)', bbox_to_anchor=(1.1, 1.35), 
                    loc='upper center', ncol=5, frameon=True, fontsize=12)

# 4. 保存图片
plt.savefig('Floyd_Comprehensive_Analysis.png', bbox_inches='tight', dpi=300)
plt.show()

print("可视化文件已保存为: Floyd_Comprehensive_Analysis.png")