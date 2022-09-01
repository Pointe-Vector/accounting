import enum
import itertools
import pandas as pd


class AccountType(str, enum.Enum):
    ASSET = "Assets"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSE = "Expenses"


def account_type(prefix):
    if prefix >= 70:
        return AccountType.EXPENSE

    if prefix >= 40:
        return AccountType.INCOME

    if prefix >= 30:
        return AccountType.EQUITY

    if prefix >= 20:
        return AccountType.LIABILITY

    return AccountType.ASSET


def main():
    parents = pd.read_csv("ucoa_parent.csv")
    subs = pd.read_csv("ucoa_sub.csv")

    df = pd.merge(
        left=subs,
        right=parents,
        how="left",
        on="Prefix",
    )

    def gen_base():
        for i in AccountType:
            yield {
                "Type": i.name.upper(),
                "Full Account Name": i.value,
                "Name": i.value,
                "Code": "",
                "Description": "",
                "Account Color": "",
                "Notes": "",
                "Symbol": "USD",
                "Namespace": "CURRENCY",
                "Hidden": "F",
                "Tax Info": "F",
                "Placeholder": "T",
            }

    def gen_parents():
        for row in parents.itertuples():
            if row.Category != "UNCATEGORIZED":
                acc_typ = account_type(row.Prefix)
                yield {
                    "Type": acc_typ.name.upper(),
                    "Full Account Name": ":".join((acc_typ, row.Category)),
                    "Name": row.Category,
                    "Code": f"{row.Prefix}00",
                    "Description": "",
                    "Account Color": "",
                    "Notes": "",
                    "Symbol": "USD",
                    "Namespace": "CURRENCY",
                    "Hidden": "F",
                    "Tax Info": "F",
                    "Placeholder": "T",
                }

    def gen_subs():
        for row in df.itertuples():
            acc_typ = account_type(row.Prefix)
            full_name = (
                ":".join((acc_typ, row.Category, row.Name))
                if row.Category != "UNCATEGORIZED"
                else ":".join((acc_typ, row.Name))
            )
            yield {
                "Type": acc_typ.name.upper(),
                "Full Account Name": full_name,
                "Name": row.Name,
                "Code": f"{row.Prefix}{row.Suffix}",
                "Description": "",
                "Account Color": "",
                "Notes": "",
                "Symbol": "USD",
                "Namespace": "CURRENCY",
                "Hidden": "F",
                "Tax Info": "F",
                "Placeholder": "T"
                if all(
                    (
                        acc_typ not in [AccountType.EXPENSE, AccountType.INCOME],
                        row.Category != "UNCATEGORIZED",
                    )
                )
                else "F",
            }

    accounts = pd.DataFrame.from_records(
        i
        for i in itertools.chain.from_iterable((gen_base(), gen_parents(), gen_subs()))
    ).sort_values("Full Account Name")
    print(accounts)
    accounts.to_csv("temp.csv", index=False)


if __name__ == "__main__":
    main()
