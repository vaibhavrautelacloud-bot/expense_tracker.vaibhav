"""charts.py - graphs using Matplotlib."""
import matplotlib.pyplot as plt
import reports
import info

COLORS = ["#0071e3", "#34c759", "#ff9f0a", "#ff3b30", "#5ac8fa", "#af52de", "#ff2d55"]


def stamp():
    """Small name + UID text in the corner of every chart."""
    plt.figtext(0.99, 0.01, f"{info.NAME}  |  UID: {info.UID}", ha="right",
                va="bottom", fontsize=8, color="gray")


def pie_chart(user, month, year):
    summary = reports.monthly_summary(user, month, year)
    if summary is None:
        return False
    data = summary["by_category"]
    plt.figure("Pie Chart", figsize=(7, 6))
    plt.pie(data.values, labels=data.index, autopct="%1.1f%%", startangle=90,
            colors=COLORS, wedgeprops={"edgecolor": "white", "linewidth": 2})
    plt.title(f"Category-wise Expenses - {reports.MONTHS[int(month)]} {year}",
              fontweight="bold")
    stamp()
    plt.show()
    return True


def bar_chart(user, month, year):
    summary = reports.monthly_summary(user, month, year)
    if summary is None:
        return False
    data = summary["by_category"]
    plt.figure("Bar Graph", figsize=(8, 5))
    bars = plt.bar(data.index, data.values, color=COLORS[:len(data)])
    plt.bar_label(bars)
    plt.xlabel("Category")
    plt.ylabel("Amount (Rs)")
    plt.title(f"Category-wise Expenses - {reports.MONTHS[int(month)]} {year}",
              fontweight="bold")
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    stamp()
    plt.show()
    return True