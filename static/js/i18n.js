(function () {
    // Check localStorage first, then fall back to HTML lang attribute
    const storedLang = localStorage.getItem('finsmart_language');
    const activeLanguage = (
        storedLang ||
        document.documentElement.lang ||
        document.body?.dataset.language ||
        "uk"
    ).toLowerCase();

    function identity(value) {
        return value;
    }

    if (activeLanguage !== "en") {
        window.translateRuntimeString = identity;
        return;
    }

    const EXACT_TRANSLATIONS = {
        "Система рекомендацій з фінансової грамотності": "Financial Literacy Recommendation System",
        "Персоналізована система для покращення ваших фінансових знань. Навчайтеся у зручний час та досягайте фінансової свободи!": "A personalized platform to improve your financial knowledge. Learn at your own pace and move toward financial freedom!",
        "Оберіть курс, який підходить саме вам — за темою та складністю": "Choose the course that fits you by topic and difficulty.",
        "Доступ до якісних освітніх матеріалів без додаткових витрат": "Access high-quality educational materials at no extra cost.",
        "Відстежуйте свій прогрес та досягнення в особистому кабінеті": "Track your progress and achievements in your profile.",
        "Оберіть курс, який підходить саме вам, та почніть свій шлях до фінансової грамотності": "Choose the course that suits you and start your path to financial literacy.",
        "Спробуйте змінити фільтри або пошуковий запит": "Try changing the filters or the search query.",
        "Перегляньте наші курси та оберіть щось для себе": "Browse our courses and pick something for yourself.",
        "Ми завжди раді відповісти на ваші запитання та допомогти вам": "We are always happy to answer your questions and help you.",
        "Заповніть форму або зв'яжіться з нами напряму": "Fill out the form or contact us directly.",
        "✅ Дякуємо, що звернулися! Ми зв'яжемося з вами найближчим часом.": "✅ Thank you for contacting us! We will get back to you soon.",
        "⚠️ Мережева помилка. Перевірте з'єднання.": "⚠️ Network error. Check your connection.",
        "Поки що немає активних повідомлень від користувачів.": "There are no active user messages yet.",
        "Поставте своє запитання, і ми відповімо вам тут.": "Ask your question and we will reply here.",
        "Людина, яка веде бюджет, накопичує в середньому в 2.5 рази більше заощаджень протягом 5 років, ніж та, яка не стежить за витратами.": "A person who keeps a budget saves on average 2.5 times more over five years than someone who does not track spending.",
        "Незнайомий продавець? Списання, яке ви не пам'ятаєте? Це сигнал перевірити картку на компрометацію.": "An unfamiliar merchant? A charge you do not remember? That is a signal to check your card for compromise.",
        "квартира, відпустка, освіта дітей — що важливо обом?": "an apartment, a vacation, children's education: what matters to both of you?",
        "Фондовий ринок для початківців": "Stock Market for Beginners",
        "Іпотека та житлові кредити": "Mortgage and Home Loans",
        "Пенсійне планування": "Retirement Planning",
        "Фінансові пастки та шахрайство": "Financial Traps and Fraud",
        "Інфляція: чому ціни ростуть": "Inflation: Why Prices Rise",
        "FinSmart: Бюджет та заощадження": "FinSmart: Budgeting and Savings",
        "FinSmart: Інвестиції для початківців": "FinSmart: Investing for Beginners",
        "FinSmart: Кредит, борги та фінансова безпека": "FinSmart: Credit, Debt, and Financial Safety",
        "Базові знання про фондовий ринок: акції, облігації, ETF. Як почати інвестувати з мінімальними ризиками.": "Basic knowledge about the stock market: stocks, bonds, and ETFs. Learn how to start investing with minimal risk.",
        "Все, що потрібно знати перед тим, як брати іпотеку. Як розрахувати переплату та вибрати найкращі умови.": "Everything you need to know before taking a mortgage. Learn how to calculate overpayment and choose the best terms.",
        "Як забезпечити собі гідну старість? Розбираємо державні та недержавні пенсійні фонди, складний відсоток.": "How can you secure a comfortable retirement? We break down public and private pension funds and compound interest.",
        "Як розпізнати фінансову піраміду, скам-проекти та захистити свої гроші від шахраїв в інтернеті.": "How to recognize a financial pyramid, scam projects, and protect your money from online fraudsters.",
        "Що таке інфляція, як вона впливає на ваші заощадження та як захистити свої гроші від знецінення.": "What inflation is, how it affects your savings, and how to protect your money from losing value.",
        "Модуль 1: Основи фінансової грамотності": "Module 1: Basics of Financial Literacy",
        "Модуль 2: Інструменти управління грошима": "Module 2: Money Management Tools",
        "Модуль 3: Інвестиції для початківців": "Module 3: Investing for Beginners",
        "Модуль 4: Довгострокова стратегія": "Module 4: Long-Term Strategy",
        "Що таке особистий бюджет?": "What is a personal budget?",
        "Правило 50/30/20": "The 50/30/20 Rule",
        "Психологія грошей": "The Psychology of Money",
        "Банківські вклади та депозити": "Bank Savings and Deposits",
        "Картки та cashback-стратегії": "Cards and Cashback Strategies",
        "Мобільні застосунки для бюджету": "Mobile Budgeting Apps",
        "Фондовий ринок: базові поняття": "Stock Market: Core Concepts",
        "ETF та диверсифікація": "ETFs and Diversification",
        "Ризики та їх мінімізація": "Risks and How to Reduce Them",
        "Пенсійне планування": "Retirement Planning",
        "Страхування та захист активів": "Insurance and Asset Protection",
        "Ваш фінансовий план на 10 років": "Your 10-Year Financial Plan",
        "Поки що немає активних повідомлень від користувачів.": "There are no active user messages yet.",
        "Що таке інфляція? - FinSmart": "What Is Inflation? - FinSmart",
        "Відправляємо...": "Sending...",
        "Надсилаємо...": "Sending...",
        "Дякуємо за відгук!": "Thank you for your review!",
        "Спробуйте ще раз.": "Please try again.",
        "Не вдалося надіслати відгук.": "Failed to send the review.",
        "Заповніть текст та оберіть рейтинг 1-5.": "Enter your review text and choose a rating from 1 to 5.",
        "Сталася помилка при збереженні результату.": "An error occurred while saving the result.",
        "✅ Правильно!": "✅ Correct!",
        "✅ Правильно! Молодець!": "✅ Correct! Well done!",
        "✅ Правильно! Чудова робота!": "✅ Correct! Great job!",
        "✅ Правильно! Чудово!": "✅ Correct! Great!",
        "✔ Правильно! Чудово!": "✔ Correct! Great!",
        "❌ Неправильно. Правильна відповідь позначена зеленим.": "❌ Incorrect. The correct answer is highlighted in green.",
        "❌ Неправильно. Правильна відповідь виділена зеленим.": "❌ Incorrect. The correct answer is highlighted in green.",
        "✖ Неправильно. Правильна відповідь позначена зеленим.": "✖ Incorrect. The correct answer is highlighted in green.",
        "Оберіть відповідь!": "Choose an answer!",
        "Що таке правило 50/30/20?": "What is the 50/30/20 rule?",
        "Коли правило 50/30/20 не підходить?": "When does the 50/30/20 rule not fit?",
        "Хто є авторкою правила 50/30/20?": "Who created the 50/30/20 rule?",
        "Навіщо відстежувати витрати?": "Why track expenses?",
        "Як правильно категоризувати витрати?": "How should you categorize expenses correctly?",
        "На скільки відсотків пересічна людина витрачає більше, ніж думає?": "By what percentage does the average person spend more than they think?",
        "Яке \"правило\" допомагає уникнути імпульсивних покупок?": "Which \"rule\" helps avoid impulse purchases?",
        "Який сервіс автоматично категоризує витрати в Україні?": "Which service automatically categorizes expenses in Ukraine?",
        "Чому депозит — це не просто \"зберігання\"?": "Why is a deposit more than just \"storage\"?",
        "Що означає стратегія \"Спочатку заплати собі\"?": "What does the \"Pay Yourself First\" strategy mean?",
        "Яким має бути розмір фінансової подушки безпеки?": "What should the size of an emergency fund be?",
        "Коли варто починати інвестувати?": "When should you start investing?",
        "Чому сімейний бюджет — це командний спорт?": "Why is a family budget a team sport?",
        "Як часто рекомендують проводити \"сімейний фінансовий мітинг\"?": "How often is it recommended to hold a \"family financial meeting\"?",
        "Яка модель сімейного бюджету вважається найбільш збалансованою?": "Which family budgeting model is considered the most balanced?",
        "Яка головна перевага гібридної моделі сімейного бюджету?": "What is the main advantage of a hybrid family budget model?",
        "Хто за що відповідає?": "Who is responsible for what?",
        "Як справедливо розподілити ролі?": "How can roles be divided fairly?",
        "Яка роль відповідає за своєчасну оплату рахунків та відсутність прострочень?": "Which role is responsible for paying bills on time and avoiding late payments?",
        "Що означає \"поріг спільного рішення\"?": "What does the \"shared decision threshold\" mean?",
        "Як часто рекомендується чергувати фінансові ролі в сім'ї?": "How often is it recommended to rotate financial roles in a family?",
        "Чи варто брати кредит на велику покупку?": "Should you take a loan for a big purchase?",
        "Як планувати великі покупки без кредиту?": "How can you plan large purchases without a loan?",
        "Якщо кредит неминучий — на що дивитися?": "If a loan is unavoidable, what should you look at?",
        "На що кредит вважається ВИПРАВДАНИМ?": "For what purpose is a loan considered JUSTIFIED?",
        "Що означає ГПС (Глобальна Процентна Ставка)?": "What does APR (Annual Percentage Rate) mean?",
        "Яка максимальна частка доходу сім'ї вважається безпечною для щомісячного кредитного платежу?": "What maximum share of family income is considered safe for a monthly loan payment?",
        "Чому сімейна подушка відрізняється від особистої?": "Why is a family emergency fund different from a personal one?",
        "Як розрахувати розмір сімейної подушки?": "How do you calculate the size of a family emergency fund?",
        "Де зберігати сімейну подушку?": "Where should you keep a family emergency fund?",
        "Де НЕ варто зберігати фінансову подушку сім'ї?": "Where should you NOT keep a family emergency fund?",
        "Коли потрібно знову поповнювати фінансову подушку?": "When should you refill an emergency fund?",
        "Яка рекомендована фінансова подушка для сім'ї з дітьми?": "What emergency fund is recommended for a family with children?",
        "Навіщо розуміти фінансові терміни?": "Why understand financial terms?",
        "Що таке \"актив\" у фінансах?": "What is an \"asset\" in finance?",
        "Що означає інфляція 10% на рік?": "What does 10% annual inflation mean?",
        "Яка формула веде до фінансового добробуту?": "Which formula leads to financial well-being?",
        "Що таке банківська виписка?": "What is a bank statement?",
        "Що потрібно шукати у виписці?": "What should you look for in a bank statement?",
        "На що слід звертати особливу увагу при аналізі регулярних витрат?": "What should you pay special attention to when analyzing recurring expenses?",
        "Що робити, якщо ви побачили у виписці незнайому операцію?": "What should you do if you see an unfamiliar transaction in your statement?",
        "Кредитна картка: друг чи ворог?": "Credit Card: Friend or Foe?",
        "Як працює кредитна картка?": "How does a credit card work?",
        "Що таке \"grace period\" (пільговий період) кредитної картки?": "What is a credit card grace period?",
        "Що категорично не рекомендується робити з кредитною карткою?": "What is strongly not recommended when using a credit card?",
        "Що таке кешбек за кредитною карткою?": "What is cashback on a credit card?",
        "Що таке фінансова незалежність?": "What is financial independence?",
        "Що означає фінансова незалежність?": "What does financial independence mean?",
        "Яке \"правило\" використовують для розрахунку цільового капіталу (FIRE)?": "Which \"rule\" is used to calculate target capital in FIRE?",
        "Коли найкраще починати рухатись до фінансової незалежності?": "When is the best time to start moving toward financial independence?",
        "Що є найважливішим етапом перед початком інвестування?": "What is the most important step before starting to invest?",
        "Що означає диверсифікація?": "What does diversification mean?",
        "Що таке кредитна історія?": "What is a credit history?",
        "Яка фінансова звичка найкорисніша?": "Which financial habit is the most useful?",
        "Що допомагає контролювати витрати?": "What helps control expenses?",
        "Що таке інфляція?": "What is inflation?",
        "Чому готівка втрачає купівельну спроможність?": "Why does cash lose purchasing power?",
        "Що може частково захищати від інфляції?": "What can partly protect you from inflation?",
        "Як інфляція впливає на заощадження?": "How does inflation affect savings?",
        "Яка практика допомагає протидіяти інфляції?": "Which practice helps counter inflation?",
        "Що таке іпотека?": "What is a mortgage?",
        "Що зазвичай визначає розмір щомісячного платежу?": "What usually determines the size of a monthly payment?",
        "Що таке LTV?": "What is LTV?",
        "Коли вигідно робити більший перший внесок?": "When is it beneficial to make a larger down payment?",
        "Що банк перевіряє в першу чергу?": "What does a bank check first?",
        "Що означає пенсійне планування?": "What does retirement planning mean?",
        "Яка перевага раннього старту накопичень?": "What is the advantage of starting savings early?",
        "Що таке диверсифікація в пенсійному портфелі?": "What is diversification in a retirement portfolio?",
        "Який інструмент частіше підходить для довгого горизонту?": "Which instrument is more suitable for a long time horizon?",
        "Яке правило внесків є практичним?": "Which contribution rule is practical?",
        "Ознака фінансового шахрайства?": "A sign of financial fraud?",
        "Як перевірити компанію перед інвестуванням?": "How do you check a company before investing?",
        "Що робити при підозрі на шахрайство?": "What should you do if you suspect fraud?",
        "Яка безпечна практика?": "Which practice is safe?",
        "Що таке акція?": "What is a stock?",
        "Який інструмент вважається найменш ризиковим?": "Which instrument is considered the least risky?",
        "Що таке ETF?": "What is an ETF?",
        "Яка основна мета диверсифікації?": "What is the main goal of diversification?",
        "Яке головне правило інвестора-початківця?": "What is the main rule for a beginner investor?"
    };

    const PHRASE_TRANSLATIONS = {
        "Система рекомендацій з фінансової грамотності": "Financial Literacy Recommendation System",
        "Наші Преміум Курси": "Our Premium Courses",
        "Відгуки наших студентів": "Reviews from Our Students",
        "Наші переваги": "Our Advantages",
        "Наші курси": "Our Courses",
        "Популярні курси": "Popular Courses",
        "Преміум Курси": "Premium Courses",
        "Контактна інформація": "Contact Information",
        "Ваш кошик порожній": "Your cart is empty",
        "Загальна сума": "Total",
        "Ваш кошик": "Your Cart",
        "Оформити замовлення": "Proceed to Checkout",
        "Перейти до курсів": "Go to Courses",
        "Зв'яжіться з нами": "Contact Us",
        "Контакти": "Contacts",
        "Про нас": "About",
        "Про FinSmart": "About FinSmart",
        "Головна": "Home",
        "Курси": "Courses",
        "Реєстрація": "Sign up",
        "Зареєструватися": "Sign up",
        "Увійти": "Log in",
        "Вийти": "Log out",
        "Профіль": "Profile",
        "Пошук курсів...": "Search courses...",
        "Всі курси": "All courses",
        "Бюджетування": "Budgeting",
        "Інвестування": "Investing",
        "Інвестиції": "Investing",
        "Кредити": "Credit",
        "Пенсії": "Pensions",
        "Почати навчання": "Start Learning",
        "Почати": "Start",
        "Переглянути": "View",
        "Детальніше": "Learn More",
        "В кошик": "Add to Cart",
        "Курси не знайдено": "No Courses Found",
        "Змінити мову": "Change language",
        "Українська": "Ukrainian",
        "Панель управління": "Admin panel",
        "Навігація": "Navigation",
        "Підтримка": "Support",
        "Центр допомоги": "Help center",
        "Політика конфіденційності": "Privacy policy",
        "Умови використання": "Terms of use",
        "Всі права захищені.": "All rights reserved.",
        "Прокрутити вгору": "Scroll to top",
        "Чат з підтримкою": "Support chat",
        "Ми онлайн, щоб допомогти": "We are online to help",
        "Закрити чат": "Close chat",
        "Напишіть повідомлення підтримці...": "Type a message to support...",
        "Відповісти користувачу...": "Reply to the user...",
        "Надіслати": "Send",
        "Панель оператора": "Operator panel",
        "Онлайн-діалоги з користувачами": "Live conversations with users",
        "Ви (адмін)": "You (admin)",
        "Користувач": "User",
        "Підтримка": "Support",
        "Забули пароль?": "Forgot your password?",
        "Ще не маєте акаунту?": "Don't have an account yet?",
        "Вже маєте акаунт?": "Already have an account?",
        "Видалити": "Remove",
        "Видалити курс?": "Delete course?",
        "Ваш Email": "Your Email",
        "НАДІСЛАТИ ЛИСТ": "SEND EMAIL",
        "Повернутися до входу": "Back to login",
        "Відновлення пароля": "Password Reset",
        "Поточний": "Current",
        "Попередній": "Previous",
        "Наступний": "Next",
        "Перевір себе": "Check yourself",
        "Тест": "Test",
        "Перевірити": "Check",
        "Ще раз": "Try again",
        "Відгук": "Review",
        "Дякуємо за проходження курсу!": "Thank you for completing the course!",
        "Поділіться враженнями — це допоможе нам зробити курс ще кращим.": "Share your impressions. This will help us make the course even better.",
        "Ви вже залишали відгук — можна оновити його нижче.": "You have already left a review. You can update it below.",
        "Надіслати": "Send",
        "Курс завершено!": "Course completed!",
        "Дякуємо за навчання. Невдовзі тут з'явиться форма відгуку.": "Thank you for learning with us. A review form will appear here soon.",
        "Матеріал уроку": "Lesson Material",
        "Фінал!": "Final!",
        "Урок": "Lesson",
        "Курс": "Course",
        "Преміум": "Premium",
        "грн": "UAH",
        "Зберегти": "Save"
    };

    const phraseEntries = Object.entries(PHRASE_TRANSLATIONS).sort(function (a, b) {
        return b[0].length - a[0].length;
    });

    function escapeRegExp(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function normalizeWhitespace(value) {
        return value.replace(/\s+/g, " ").trim();
    }

    function translateCore(core) {
        const normalized = normalizeWhitespace(core);
        if (!normalized) {
            return core;
        }

        let translated = EXACT_TRANSLATIONS[normalized] || normalized;

        for (const pair of phraseEntries) {
            translated = translated.replace(new RegExp(escapeRegExp(pair[0]), "g"), pair[1]);
        }

        return translated;
    }

    function translateRuntimeString(value) {
        if (typeof value !== "string") {
            return value;
        }

        const leading = (value.match(/^\s*/) || [""])[0];
        const trailing = (value.match(/\s*$/) || [""])[0];
        const core = value.slice(leading.length, value.length - trailing.length);

        if (!core.trim()) {
            return value;
        }

        return leading + translateCore(core) + trailing;
    }

    function shouldSkipTextNode(node) {
        const parent = node.parentElement;
        if (!parent) {
            return true;
        }

        return Boolean(parent.closest("script, style, noscript, code, pre, textarea"));
    }

    function translateTextNode(node) {
        if (shouldSkipTextNode(node)) {
            return;
        }

        const translated = translateRuntimeString(node.nodeValue);
        if (translated !== node.nodeValue) {
            node.nodeValue = translated;
        }
    }

    function translateAttributes(element) {
        const attrs = ["placeholder", "title", "aria-label", "alt"];
        for (const attr of attrs) {
            if (element.hasAttribute(attr)) {
                const current = element.getAttribute(attr);
                const translated = translateRuntimeString(current);
                if (translated !== current) {
                    element.setAttribute(attr, translated);
                }
            }
        }

        if (
            element instanceof HTMLInputElement &&
            ["button", "submit", "reset"].includes(element.type)
        ) {
            const translated = translateRuntimeString(element.value);
            if (translated !== element.value) {
                element.value = translated;
            }
        }
    }

    function translateTree(root) {
        if (!root) {
            return;
        }

        if (root.nodeType === Node.TEXT_NODE) {
            translateTextNode(root);
            return;
        }

        if (root.nodeType !== Node.ELEMENT_NODE) {
            return;
        }

        translateAttributes(root);

        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
        let current = walker.nextNode();
        while (current) {
            translateTextNode(current);
            current = walker.nextNode();
        }

        root.querySelectorAll("*").forEach(translateAttributes);
    }

    window.translateRuntimeString = translateRuntimeString;

    function applyTranslations() {
        translateTree(document.body);
        document.title = translateRuntimeString(document.title);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", applyTranslations);
    } else {
        applyTranslations();
    }

    const observer = new MutationObserver(function (mutations) {
        for (const mutation of mutations) {
            if (mutation.type === "characterData") {
                translateTextNode(mutation.target);
                continue;
            }

            if (mutation.type === "attributes" && mutation.target instanceof Element) {
                translateAttributes(mutation.target);
                continue;
            }

            for (const node of mutation.addedNodes) {
                translateTree(node);
            }
        }
    });

    function startObserver() {
        if (!document.body) {
            return;
        }

        observer.observe(document.body, {
            subtree: true,
            childList: true,
            characterData: true,
            attributes: true,
            attributeFilter: ["placeholder", "title", "aria-label", "alt", "value"]
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", startObserver);
    } else {
        startObserver();
    }
})();
