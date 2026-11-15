# Author: Aidan Guenther
"""Render the events-by-service figure for the paper."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS = os.path.join(ROOT, "data/processed/events.csv")
OUT = os.path.join(ROOT, "report/figures/events_by_service.png")

def main():
    df = pd.read_csv(EVENTS)
    # count events for each (service, event_type) pair
    pivot = df.pivot_table(index="service", columns="event_type",
                           values="ts", aggfunc="count", fill_value=0)
    ax = pivot.plot(kind="bar", stacked=True, figsize=(8, 5))
    ax.set_xlabel("Service")
    ax.set_ylabel("Event count")
    ax.set_title("Honeypot events by service and type")
    ax.legend(title="Event type", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    plt.savefig(OUT, dpi=150)
    print(f"figure -> {OUT}")

if __name__ == "__main__":
    main()