from config import RESULT_FILE

def save_results(results, filename=RESULT_FILE):

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:
            
            f.write("=" * 80 + "\n")
            f.write("نتایج استخراج نامه‌ها\n")
            f.write("=" * 80 + "\n\n")

            for i, result in enumerate(results, 1):

                f.write("=" * 80 + "\n")
                f.write(f"نامه {i}\n")
                f.write("=" * 80 + "\n")
                f.write(
                    f"شماره: "
                    f"{result.get('letter_number', '')}\n"
                )
                f.write(
                    f"تاریخ: "
                    f"{result.get('date', '')}\n"
                )
                f.write(
                    f"ساعت: "
                    f"{result.get('time', '')}\n"
                )
                f.write(
                    f"موضوع: "
                    f"{result.get('title', '')}\n"
                )
                f.write("-" * 80 + "\n")
                f.write("متن:\n")
                f.write(result.get("text", ""))
                f.write("\n\n")

        print(f"✅ نتایج در فایل {filename} ذخیره شد.")

    except Exception as e:
        print(f"❌ خطا در ذخیره نتایج: {e}")

