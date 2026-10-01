with open('frontend/src/__tests__/MultiTenancy.test.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('import { render, screen, waitFor } from \'@testing-library/react\'', 'import { render, screen } from \'@testing-library/react\'')

with open('frontend/src/__tests__/MultiTenancy.test.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
