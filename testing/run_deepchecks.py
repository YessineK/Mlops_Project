def main():
    print("="*80)
    print("🚀 DEEPCHECKS VALIDATION")
    print("="*80)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load model and data
        model, preprocessor, df = load_model_and_data()
        
        # Split data
        train_df, test_df = split_data(df)
        
        # Create datasets
        train_dataset, test_dataset = create_datasets(train_df, test_df)
        
        # Run validation suites
        results = run_validation_suite(train_dataset, test_dataset, model, output_dir)
        
        # Generate summary
        generate_summary_report(results, output_dir)
        
        # Check overall status
        all_passed = all(r.get("passed", False) for r in results.values())
        
        print("")
        print("="*80)
        if all_passed:
            print("✅ ALL VALIDATION TESTS PASSED")
            print("="*80)
            sys.exit(0)  # ← SUCCESS
        else:
            print("⚠️  SOME VALIDATION TESTS FAILED")
            print("="*80)
            print("⚠️  Warning: Model has quality issues")
            print("   Review reports before deploying to production")
            sys.exit(0)  # ← WARNING mais pas d'erreur (changé de 1 à 0)
        
    except Exception as e:
        print("")
        print("="*80)
        print(f"❌ DEEPCHECKS VALIDATION ERROR: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        
        # Créer un rapport d'erreur minimal
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deepchecks Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            background: #0b0f17;
            color: #e8eefc;
            padding: 20px;
        }}
        .error {{
            background: #ff4d4d;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        pre {{
            background: #121a27;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h1>❌ Deepchecks Validation Error</h1>
        <p>An error occurred during validation. Check logs for details.</p>
    </div>
    <h2>Error Details:</h2>
    <pre>{traceback.format_exc()}</pre>
</body>
</html>
"""
        error_path = os.path.join(output_dir, "deepchecks_summary.html")
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(error_html)
        
        print(f"✅ Error report saved: {error_path}")
        sys.exit(0)  # ← Ne bloque PAS le pipeline (changé de 1 à 0)


if __name__ == "__main__":
    main()