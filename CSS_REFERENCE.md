# KB Helper CSS Reference Guide

Quick reference for using the modernized CSS classes and design tokens.

---

## 🎨 Design Tokens (CSS Variables)

### Colors

#### Primary (Blues)
```css
--primary-50: #e3f2fd    /* Lightest - backgrounds */
--primary-500: #2196f3   /* Main brand color */
--primary-700: #1976d2   /* Headers, important text */
--primary-800: #1565c0   /* Dark accents */
```

#### Accent Colors
```css
--accent-green: #4caf50      /* Success, positive */
--accent-green-light: #81c784
--accent-green-dark: #388e3c

--accent-orange: #ff9800     /* Warning, medium priority */
--accent-purple: #9c27b0     /* Duplicates, special */
--accent-teal: #009688       /* Info, metrics */
--accent-red: #f44336        /* Error, high priority */
```

#### Neutrals
```css
--gray-50: #fafafa      /* Backgrounds */
--gray-100: #f5f5f5
--gray-200: #eeeeee     /* Borders */
--gray-300: #e0e0e0
--gray-600: #757575     /* Secondary text */
--gray-700: #616161     /* Primary text */
--gray-900: #212121     /* Headings */
```

### Spacing
```css
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px
--spacing-2xl: 48px
--spacing-3xl: 64px

/* Usage */
padding: var(--spacing-xl);
margin-bottom: var(--spacing-lg);
```

### Border Radius
```css
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px        /* Default for cards */
--radius-xl: 16px
--radius-full: 9999px    /* Pills, circles */

/* Usage */
border-radius: var(--radius-lg);
```

### Shadows
```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
--shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1)      /* Default cards */
--shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1)    /* Hover */
--shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1)
--shadow-2xl: 0 25px 50px -12px rgba(0,0,0,0.25) /* Maximum depth */

/* Usage */
box-shadow: var(--shadow-md);
```

### Transitions
```css
--transition-fast: 150ms ease-in-out
--transition-base: 250ms ease-in-out
--transition-slow: 350ms ease-in-out

/* Usage */
transition: all var(--transition-base);
```

---

## 🏗️ Layout Classes

### Container
```html
<div class="container">
    <!-- Max-width: 1280px, centered, padding: 24px -->
</div>
```

### Grid (Materialize)
```html
<div class="row">
    <div class="col s12 m6 l4">
        <!-- 12 cols mobile, 6 tablet, 4 desktop -->
    </div>
</div>
```

---

## 🎴 Card Components

### Basic Card
```html
<div class="card">
    <!-- Rounded corners, shadow, white background -->
    <div class="card-content">
        <span class="card-title">Title</span>
        <p>Content here...</p>
    </div>
    <div class="card-action">
        <a href="#">Action</a>
    </div>
</div>
```

### Statistics Card
```html
<div class="stat-card stat-card-blue">
    <i class="material-icons stat-icon">article</i>
    <div class="stat-number">105</div>
    <div class="stat-label">Total Articles</div>
</div>
```

**Available variants:**
- `.stat-card-blue` - Primary metrics
- `.stat-card-orange` - Warnings, medium
- `.stat-card-red` - Errors, high priority
- `.stat-card-teal` - Info metrics
- `.stat-card-green` - Success, positive
- `.stat-card-purple` - Special categories

### Feature Card (Home Page)
```html
<div class="feature-card feature-card-green">
    <div class="card-content white-text">
        <span class="card-title">
            <i class="material-icons">check</i>
            Feature Name
        </span>
        <p>Description...</p>
    </div>
    <div class="card-action">
        <a href="#" class="white-text">Action</a>
    </div>
</div>
```

**Variants:**
- `.feature-card-blue` - Analysis features
- `.feature-card-green` - Success/completion features
- `.feature-card-purple` - Special features
- `.feature-card-grey` - Coming soon/disabled

### Form Card
```html
<div class="form-card">
    <div class="card-content">
        <span class="card-title">
            <i class="material-icons">settings</i>
            Form Title
        </span>
        <form>
            <!-- Form content -->
        </form>
    </div>
    <div class="card-action">
        <button class="btn">Submit</button>
    </div>
</div>
```

### Table Card
```html
<div class="table-card">
    <div class="card-content">
        <span class="card-title">
            <span><i class="material-icons">list</i> Table Title</span>
        </span>

        <div class="export-buttons">
            <button class="btn green">Export CSV</button>
            <button class="btn blue">Export JSON</button>
        </div>

        <table class="striped highlight responsive-table">
            <!-- Table content -->
        </table>
    </div>
</div>
```

---

## 🔘 Buttons

### Standard Button
```html
<button class="btn waves-effect waves-light blue">
    <i class="material-icons left">search</i>
    Button Text
</button>
```

### Button Variants
```html
<!-- Primary -->
<button class="btn btn-primary">Primary</button>

<!-- Success -->
<button class="btn green">Success</button>

<!-- Warning -->
<button class="btn orange">Warning</button>

<!-- Danger -->
<button class="btn red">Danger</button>

<!-- Small -->
<button class="btn-small blue">Small</button>

<!-- Large -->
<button class="btn-large blue">Large</button>
```

---

## 📊 Data Visualization

### Similarity Meter (Duplicates)
```html
<div class="similarity-meter">
    <span class="similarity-label">
        <i class="material-icons">analytics</i>
        Title Similarity
    </span>
    <div class="similarity-bar">
        <div class="similarity-fill high" style="width: 85%"></div>
    </div>
    <span class="similarity-value">85%</span>
</div>
```

**Fill variants:**
- `.similarity-fill.high` - Green gradient (>70%)
- `.similarity-fill.medium` - Orange gradient (40-70%)
- `.similarity-fill.low` - Grey gradient (<40%)

### Confidence Badge
```html
<span class="confidence-badge confidence-high">
    <i class="material-icons">priority_high</i>
    High
</span>
```

**Variants:**
- `.confidence-high` - Red gradient
- `.confidence-medium` - Orange gradient
- `.confidence-low` - Yellow gradient

### Chip/Badge
```html
<span class="chip high">
    <i class="material-icons">warning</i>
    High Priority
</span>
```

**Variants:**
- `.chip.high` - Red (urgent)
- `.chip.medium` - Orange (moderate)
- `.chip.low` - Green (low priority)

---

## 📝 Typography

### Headings
```html
<h1>Page Title</h1>        <!-- 2.5rem, weight 300 -->
<h2>Section Title</h2>      <!-- 2rem, weight 300 -->
<h3>Subsection</h3>         <!-- 1.75rem, weight 400 -->
<h4>Card Title</h4>         <!-- 1.5rem, weight 400 -->
<h5>Small Heading</h5>      <!-- 1.25rem, weight 500 -->
<h6>Smallest Heading</h6>   <!-- 1rem, weight 500 -->
```

### Paragraph
```html
<p>Regular paragraph text with 1.625 line height</p>
<p class="flow-text">Large body text (1.25rem)</p>
```

### Utility Classes
```html
<!-- Alignment -->
<p class="text-center">Centered text</p>
<p class="text-left">Left aligned</p>
<p class="text-right">Right aligned</p>

<!-- Font Weight -->
<span class="font-light">Light (300)</span>
<span class="font-normal">Normal (400)</span>
<span class="font-medium">Medium (500)</span>
<span class="font-semibold">Semibold (600)</span>
<span class="font-bold">Bold (700)</span>
```

---

## 📱 Page-Specific Components

### Hero Section (Home Page)
```html
<div class="hero-section">
    <h3>
        <i class="material-icons hero-icon">dashboard</i>
        Welcome Message
    </h3>
    <p class="flow-text">Subtitle text</p>
</div>
```

### Analysis Header
```html
<div class="analysis-header">
    <h3>
        <i class="material-icons header-icon">schedule</i>
        Page Title
    </h3>
    <p class="flow-text">Description</p>
</div>
```

### Duplicate Pair Card
```html
<div class="duplicate-pair-card">
    <div class="card-content">
        <div class="pair-header">
            <h5>
                <i class="material-icons">content_copy</i>
                Duplicate Pair #1
            </h5>
            <span class="confidence-badge confidence-high">
                <i class="material-icons">priority_high</i>
                High Confidence
            </span>
        </div>

        <div class="similarity-metrics">
            <!-- Similarity meters here -->
        </div>

        <div class="article-comparison">
            <div class="article-box">
                <h6><i class="material-icons">article</i> Article 1</h6>
                <div class="article-info">
                    <p><strong>ID:</strong> HE-123</p>
                    <p><strong>Title:</strong> <a href="#">Article Title</a></p>
                </div>
            </div>
            <div class="article-box">
                <h6><i class="material-icons">article</i> Article 2</h6>
                <div class="article-info">
                    <p><strong>ID:</strong> HE-456</p>
                    <p><strong>Title:</strong> <a href="#">Article Title</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Message Card
```html
<div class="message-card success white-text">
    <i class="material-icons">check_circle</i>
    <span>Success message</span>
</div>
```

**Variants:**
- `.message-card.success` - Green gradient
- `.message-card.error` - Red gradient
- `.message-card.warning` - Orange gradient
- `.message-card.info` - Blue gradient

### Status Card
```html
<div class="status-card">
    <div class="card-content">
        <span class="card-title">
            <i class="material-icons">info</i>
            Connection Status
        </span>
        <p><strong>Connected to:</strong> youtrack.example.com</p>
        <p class="status-indicator">
            <i class="material-icons">check_circle</i>
            Credentials configured
        </p>
    </div>
</div>
```

---

## 📋 Forms

### Input Field (Materialize)
```html
<div class="input-field">
    <i class="material-icons prefix">folder</i>
    <input id="project_id" name="project_id" type="text" required class="validate">
    <label for="project_id">Project ID</label>
    <span class="helper-text">Helper text here</span>
</div>
```

---

## 📊 Tables

### Enhanced Table
```html
<table class="striped highlight responsive-table">
    <thead>
        <tr>
            <th class="sortable" data-sort="id">
                ID <i class="material-icons tiny">unfold_more</i>
            </th>
            <th class="sortable" data-sort="title">
                Title <i class="material-icons tiny">unfold_more</i>
            </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>HE-123</td>
            <td><a href="#">Article Title</a></td>
        </tr>
    </tbody>
</table>
```

---

## 🎯 Loading States

### Loading Section
```html
<div id="loadingSection" style="display: none;">
    <div class="row">
        <div class="col s12 center-align">
            <div class="preloader-wrapper big active">
                <div class="spinner-layer spinner-blue-only">
                    <div class="circle-clipper left">
                        <div class="circle"></div>
                    </div>
                    <div class="gap-patch">
                        <div class="circle"></div>
                    </div>
                    <div class="circle-clipper right">
                        <div class="circle"></div>
                    </div>
                </div>
            </div>
            <p class="flow-text">Loading...</p>
        </div>
    </div>
</div>
```

---

## 🎨 Common Patterns

### Card with Icon Header
```html
<div class="card">
    <div class="card-content">
        <span class="card-title">
            <i class="material-icons">icon_name</i>
            Title Here
        </span>
        <p>Content...</p>
    </div>
</div>
```

### Gradient Background
```css
background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-700) 100%);
```

### Hover Effect
```css
.my-element {
    transition: all var(--transition-base);
}

.my-element:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}
```

### Accent Border
```css
.my-card {
    border-left: 4px solid var(--primary-500);
    /* or */
    border-top: 4px solid var(--accent-orange);
}
```

---

## 🛠️ Utility Classes

### Spacing Utilities
```html
<!-- Margin Top -->
<div class="mt-0">No margin top</div>
<div class="mt-1">4px margin top</div>
<div class="mt-2">8px margin top</div>
<div class="mt-3">16px margin top</div>
<div class="mt-4">24px margin top</div>
<div class="mt-5">32px margin top</div>

<!-- Margin Bottom -->
<div class="mb-0">No margin bottom</div>
<div class="mb-1">4px margin bottom</div>
<!-- ... same pattern ... -->
```

---

## 📱 Responsive Utilities (Materialize)

### Show/Hide by Screen Size
```html
<!-- Hide on mobile -->
<div class="hide-on-small-only">Desktop only</div>

<!-- Hide on tablet and up -->
<div class="hide-on-med-and-up">Mobile only</div>

<!-- Hide on desktop -->
<div class="hide-on-large-only">Mobile and tablet</div>
```

### Grid Responsive Columns
```html
<div class="col s12 m6 l4">
    <!-- s12: Full width on mobile (< 600px)
         m6:  Half width on tablet (600px - 992px)
         l4:  Third width on desktop (> 992px) -->
</div>
```

---

## 🎨 Quick Copy-Paste Examples

### Blue Statistics Card
```html
<div class="stat-card stat-card-blue">
    <i class="material-icons stat-icon">article</i>
    <div class="stat-number">105</div>
    <div class="stat-label">Total Articles</div>
</div>
```

### Primary Button with Icon
```html
<button class="btn waves-effect waves-light blue" type="submit">
    <i class="material-icons left">search</i>
    Analyze
</button>
```

### Export Button Group
```html
<div class="export-buttons">
    <button class="btn waves-effect waves-light green" onclick="exportToCSV()">
        <i class="material-icons left">download</i>Export CSV
    </button>
    <button class="btn waves-effect waves-light blue" onclick="exportToJSON()">
        <i class="material-icons left">download</i>Export JSON
    </button>
</div>
```

### Feature Grid
```html
<div class="feature-grid">
    <div class="feature-card feature-card-blue">
        <!-- Card content -->
    </div>
    <div class="feature-card feature-card-green">
        <!-- Card content -->
    </div>
    <div class="feature-card feature-card-purple">
        <!-- Card content -->
    </div>
</div>
```

---

## 📚 File References

- **Base Styles**: `analyzer/static/analyzer/css/base.css`
- **Home Page**: `analyzer/static/analyzer/css/index.css`
- **Analysis Pages**: `analyzer/static/analyzer/css/analysis.css`
- **Duplicates Page**: `analyzer/static/analyzer/css/duplicates.css`

---

## 💡 Pro Tips

1. **Always use CSS variables** for colors, spacing, shadows
2. **Stick to the spacing scale** (4px, 8px, 16px, 24px, 32px)
3. **Use Materialize grid** for responsive layouts
4. **Add transitions** to all interactive elements
5. **Include icons** for better visual communication
6. **Test on mobile** - resize browser to check responsive behavior
7. **Use semantic colors** - green for success, red for errors, etc.

---

**Quick Start**: Copy any example above and modify the content. All classes are ready to use!

**Last Updated**: 2025-11-23
