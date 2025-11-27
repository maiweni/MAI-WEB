export const categories = [
  {
    key: 'ai',
    title: 'AI算法',
    description: '大模型、检索增强、优化与部署的实战笔记。',
    matchers: ['ai算法', 'ai', '算法', '模型', '大模型', '机器学习', '深度学习'],
  },
  {
    key: 'paper',
    title: '论文阅读',
    description: '论文精读、要点摘录与复现心得。',
    matchers: ['论文阅读', '论文', 'paper', 'paper reading'],
  },
  {
    key: 'dev',
    title: '软件开发',
    description: '工程化、工具链、自动化与交付实践。',
    matchers: ['软件开发', '开发', '工程', '工程化', 'dev', '工具', '部署'],
  },
  {
    key: 'other',
    title: '其他',
    description: '暂未归类的记录与思考。',
    matchers: [],
  },
]

export const normalizeTags = (value) => {
  if (!value) return []
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean)
  }
  if (typeof value === 'string') {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
  }
  return []
}

export const resolveCategoryKey = (tags) => {
  if (!tags.length) return 'other'
  const lowerTags = tags.map((tag) => tag.toLowerCase())
  for (const category of categories) {
    if (category.key === 'other') continue
    const matched = category.matchers.some((keyword) =>
      lowerTags.some((tag) => tag.includes(keyword.toLowerCase()))
    )
    if (matched) return category.key
  }
  return 'other'
}

export const getCategoryMeta = (key) => categories.find((item) => item.key === key)

