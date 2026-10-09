import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from mango_disease_ai import analyze, generate_pdf
import base64

IMAGE = r'E:\AIUB R&D ICCA\Amrapali Mango Diseases Dataset\Amrapali Mango Diseases Dataset\Anthracnose\Anthracnose_001.jpg'

print('=' * 60)
print('  mango-disease-ai LIVE DEMO')
print('=' * 60)
print('Image: Anthracnose_001.jpg')
print('Loading AI models... (takes ~30s first time)')
print()

result = analyze(IMAGE)

if not result['is_mango']:
    print('Not a mango image!')
else:
    conf = result['mango_confidence']
    pred = result['predicted_class']
    pred_conf = result['confidence']

    print(f'MANGO DETECTED     : {conf:.1%} confidence')
    print(f'DISEASE PREDICTED  : {pred}')
    print(f'CONFIDENCE         : {pred_conf:.1%}')
    print()
    print('ALL SCORES:')
    for s in result['all_scores']:
        bar = '#' * int(s['score'] * 25)
        print(f'  {s["class"]:20s} {s["score"]*100:5.1f}%  {bar}')
    print()

    # Save heatmap
    heatmap = base64.b64decode(result['gradcam_base64'])
    with open('heatmap_output.png', 'wb') as f:
        f.write(heatmap)
    print('Grad-CAM heatmap  -> heatmap_output.png')

    # Generate PDF
    pdf = generate_pdf(result, user_name='Dr. Arpon')
    with open('mango_diagnosis_report.pdf', 'wb') as f:
        f.write(pdf)
    print('PDF report         -> mango_diagnosis_report.pdf')
    print()
    print('ALL DONE!')
