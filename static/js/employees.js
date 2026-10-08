/* The page receives scoped database records from Django; writes require CSRF. */
(() => {
    "use strict";
    const body = document.body;
    if (!body.classList.contains("cc-app")) return;
    // Đọc bản dữ liệu đã được Django giới hạn quyền và gắn vào trang; đây là dữ liệu database, không phải bộ demo trong trình duyệt.
    const seed = JSON.parse(document.getElementById("employees-bootstrap").textContent);
    const state = seed;
    const page = body.dataset.page;
    const recordId = body.dataset.recordId;
    const role = body.dataset.role;
    const root = body.dataset.root;
    const iconRoot = body.dataset.iconRoot;
    const $ = (selector, scope = document) => scope.querySelector(selector);
    const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
    // Biến ký tự đặc biệt thành chữ hiển thị an toàn trước khi ghép dữ liệu vào HTML.
    const escape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));

    // Lưu dùng POST có mã chống giả mạo yêu cầu; chờ máy chủ xác nhận rồi mới chuyển về trang danh sách.
    async function submit(form, endpoint, input, destination) {
        // Chặn bấm lưu nhiều lần khi yêu cầu trước vẫn đang chờ kết quả.
        if (form.dataset.saving) return;
        form.dataset.saving = "true";
        const button = $('[type="submit"]', form);
        button.disabled = true;
        try {
            const response = await fetch(url(endpoint), {
                method: "POST", credentials: "same-origin",
                headers: {"Content-Type": "application/json", "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').value},
                body: JSON.stringify(input),
            });
            // Phiên hết hạn thì quay lại đăng nhập; giữ địa chỉ trang hiện tại trong next để quay lại sau.
            if (response.status === 401) {
                location.assign(body.dataset.loginUrl + "?next=" + encodeURIComponent(location.pathname + location.search));
                return;
            }
            const result = await response.json().catch(() => ({error: "Không thể lưu. Vui lòng tải lại trang và thử lại."}));
            if (!response.ok) { error(form, result.error || "Không thể lưu dữ liệu."); return; }
            go(destination);
        } catch (_) {
            error(form, "Không kết nối được máy chủ. Vui lòng thử lại.");
        // Dù thành công hay lỗi, mở lại nút lưu; việc chờ mạng không được để biểu mẫu khóa vĩnh viễn.
        } finally {
            button.disabled = false;
            delete form.dataset.saving;
        }
    }
    // Ngày nhập/kiểm tra nhanh theo giờ Việt Nam; máy chủ vẫn kiểm tra lại bằng ngày của chính nó.
    function today() {
        const parts = new Intl.DateTimeFormat("en-CA", {timeZone: "Asia/Ho_Chi_Minh", year: "numeric", month: "2-digit", day: "2-digit"}).formatToParts(new Date());
        const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
        return values.year + "-" + values.month + "-" + values.day;
    }
    function date(value) { return value ? value.split("-").reverse().join("/") : "—"; }
    // Định dạng chuỗi số để giữ hai chữ số thập phân; không đổi lương sang Number chỉ để trình bày.
    function money(value) {
        const [integer, decimal = "00"] = String(value).split(".");
        return integer.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (decimal === "00" ? "" : "," + decimal) + " VNĐ";
    }
    // Bỏ dấu và đổi chữ thường giúp tìm Hà bằng từ khóa ha; chỉ dùng cho tìm kiếm, không sửa tên đang lưu.
    function normalize(value) { return String(value ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase(); }
    function url(path = "") {
        return new URL(root + path, location.origin).pathname;
    }
    function go(path) { location.assign(url(path)); }
    let toastTimer;
    function toast(message, error = false) {
        const target = $("#toast");
        target.textContent = message;
        target.style.color = error ? "#bd193d" : "";
        target.hidden = false;
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { target.hidden = true; }, 5000);
    }
    function icon(name, pink = false) {
        return '<span' + (pink ? ' class="cc-pink-icon"' : "") + '><img class="cc-icon" src="' + escape(iconRoot + name + ".svg") + '" alt="" aria-hidden="true"></span>';
    }
    const employee = id => state.employees.find(item => item.id === id);
    const currentUser = seed.currentUser;
    function contractStatus(contract) { return contract.status; }
    function statusBadge(status, contract = false) {
        const labels = contract
            ? {active: "Đang hiệu lực", expiring: "Sắp hết hạn", expired: "Đã hết hạn", upcoming: "Chưa hiệu lực", terminated: "Chấm dứt"}
            : {active: "Đang làm việc", inactive: "Đã nghỉ việc"};
        return '<span class="cc-badge cc-badge-' + escape(status === "upcoming" ? "inactive" : status) + '">' + escape(labels[status]) + "</span>";
    }
    function options(values, firstLabel, selected = "") {
        return (firstLabel !== null ? '<option value="">' + escape(firstLabel) + "</option>" : "") +
            values.map(value => '<option value="' + escape(value) + '"' + (value === selected ? " selected" : "") + ">" + escape(value) + "</option>").join("");
    }
    function error(form, message) {
        const target = $(".cc-form-error", form);
        target.textContent = message;
        target.hidden = false;
        target.scrollIntoView({block: "nearest", behavior: "instant"});
    }
    function missing(target, label, backPath = "") {
        target.innerHTML = '<section class="cc-panel cc-empty-panel"><h2>Không tìm thấy ' + escape(label) + '</h2><p>Thông tin này không có trong danh sách hiện tại.</p><a class="cc-button cc-button-secondary" href="' + url(backPath) + '">Quay lại danh sách</a></section>';
    }
    // Nối menu và thông tin tài khoản với dữ liệu nhận từ máy chủ; đổi giao diện không đổi quyền trên máy chủ.
    function initShell() {
        const staff = role === "staff";
        $("[data-page]").classList.toggle("cc-my-contracts", page === "my-contracts");
        $("#role-label").textContent = staff ? "Nhân viên" : "Quản lý";
        $("#nav-caption").textContent = staff ? "KHÔNG GIAN NHÂN VIÊN" : "KHÔNG GIAN QUẢN LÝ";
        $$("[data-user-name]").forEach(el => { el.textContent = seed.account.name; });
        $$("[data-user-job]").forEach(el => { el.textContent = seed.account.job; });
        $$("[data-avatar]").forEach(el => { el.textContent = seed.account.initials; });
        const profiles = $('[data-nav="employees"]');
        const contracts = $('[data-nav="contracts"]');
        if (staff) {
            $(".cc-nav-item:disabled").hidden = true;
            profiles.href = url("me/");
            $("span", profiles).textContent = "Hồ sơ của tôi";
            $("img", profiles).src = iconRoot + "user.svg";
            contracts.href = url("me/contracts/");
            $("span", contracts).textContent = "Hợp đồng của tôi";
        }
        const active = page.includes("contract") ? contracts : profiles;
        active.classList.add("active");
        active.setAttribute("aria-current", "page");
        const accountMenu = $("#account-menu");
        $("#account-toggle").addEventListener("click", () => {
            accountMenu.hidden = !accountMenu.hidden;
            $("#account-toggle").setAttribute("aria-expanded", String(!accountMenu.hidden));
        });
        $$("[data-own-link]").forEach(link => {
            if ((page === "my-profile" && link.pathname.endsWith("/me/")) ||
                (page === "my-contracts" && link.pathname.endsWith("/me/contracts/"))) link.setAttribute("aria-current", "page");
        });
        document.addEventListener("click", event => {
            if (!event.target.closest(".cc-account")) {
                accountMenu.hidden = true;
                $("#account-toggle").setAttribute("aria-expanded", "false");
            }
            $$(".cc-actions[open]").forEach(menu => { if (!menu.contains(event.target)) menu.open = false; });
            if (body.classList.contains("cc-menu-open") && !event.target.closest(".cc-sidebar, #mobile-menu")) {
                body.classList.remove("cc-menu-open");
                $("#mobile-menu").setAttribute("aria-expanded", "false");
            }
        });
        document.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                if (!accountMenu.hidden) $("#account-toggle").focus();
                accountMenu.hidden = true;
                $("#account-toggle").setAttribute("aria-expanded", "false");
                body.classList.remove("cc-menu-open");
                $("#mobile-menu").setAttribute("aria-expanded", "false");
                $$(".cc-actions[open]").forEach(menu => { menu.open = false; });
            }
        });
        // Đặt menu thao tác trong vùng nhìn thấy; đóng khi cuộn/đổi kích thước để tránh menu nằm lệch hàng.
        document.addEventListener("toggle", event => {
            const menu = event.target;
            if (!menu.matches(".cc-actions[open]")) return;
            const anchor = $("summary", menu).getBoundingClientRect();
            const panel = $("div", menu);
            panel.style.right = Math.max(12, innerWidth - anchor.right) + "px";
            panel.style.top = Math.max(8, Math.min(anchor.bottom + 4, innerHeight - panel.offsetHeight - 8)) + "px";
        }, true);
        const closeActions = () => { $$(".cc-actions[open]").forEach(menu => { menu.open = false; }); };
        window.addEventListener("resize", closeActions);
        window.addEventListener("scroll", closeActions, true);
        $("#mobile-menu").addEventListener("click", () => {
            const open = body.classList.toggle("cc-menu-open");
            $("#mobile-menu").setAttribute("aria-expanded", String(open));
        });
        $("#notifications").addEventListener("click", () => { toast("Bạn không có thông báo mới."); });
        $("#global-search").addEventListener("keydown", event => {
            if (event.key !== "Enter") return;
            const value = event.target.value.trim();
            if (!value) return;
            if (staff) { toast(normalize(seed.account.name).includes(normalize(value)) ? "Thông tin của bạn được hiển thị trong Hồ sơ của tôi." : "Không tìm thấy thông tin phù hợp."); return; }
            const path = page.includes("contract") ? "contracts/" : "";
            const destination = new URL(url(path), location.origin);
            destination.searchParams.set("q", value);
            location.assign(destination.pathname + destination.search);
        });
        if (seed.messages.length) toast(seed.messages.join(" · "));
    }
    // Mỗi trang có bốn dòng; chỉ chia mảng đang có, không gửi một yêu cầu tìm kiếm database cho từng trang.
    function paginate(target, total, selected, change) {
        const pages = Math.max(1, Math.ceil(total / 4));
        let html = '<button type="button" data-page-number="' + (selected - 1) + '" aria-label="Trang trước"' + (selected === 1 ? " disabled" : "") + ">‹</button>";
        for (let i = 1; i <= pages; i++) html += '<button type="button" data-page-number="' + i + '" class="' + (i === selected ? "active" : "") + '" aria-label="Trang ' + i + '"' + (i === selected ? ' aria-current="page"' : "") + ">" + i + "</button>";
        html += '<button type="button" data-page-number="' + (selected + 1) + '" aria-label="Trang sau"' + (selected === pages ? " disabled" : "") + ">›</button>";
        target.innerHTML = html;
        $$("button", target).forEach(button => { button.addEventListener("click", () => { change(Number(button.dataset.pageNumber)); }); });
    }
    // Nút vô hiệu hóa chỉ hiện với hồ sơ đang làm việc; các nút sửa vẫn phải qua kiểm tra phía máy chủ.
    function actions(item, kind) {
        const path = kind === "employee" ? item.id + "/" : "contracts/" + item.id + "/";
        const deactivate = kind === "employee" && item.status === "active"
            ? '<button type="button" class="cc-danger-text" data-deactivate="' + escape(item.id) + '">Vô hiệu hóa hồ sơ</button>' : "";
        return '<details class="cc-actions"><summary role="button" aria-label="Thao tác với ' + escape(item.id) + '">⋮</summary><div><a href="' + url(path) + '">Xem chi tiết</a><a href="' + url(path + "edit/") + '">' + (kind === "employee" ? "Chỉnh sửa hồ sơ" : "Chỉnh sửa / Gia hạn") + "</a>" + deactivate + "</div></details>";
    }
    // Lọc danh sách đã tải theo mã/tên, phòng ban, chức vụ, trạng thái; thay bộ lọc đưa về trang đầu.
    function initEmployeeList() {
        let selectedPage = 1;
        $("#department-filter").innerHTML = options(state.departments, "Phòng ban");
        $("#job-filter").innerHTML = options(state.jobs, "Chức vụ");
        $("#employee-search").value = new URLSearchParams(location.search).get("q") || "";
        function render() {
            const query = normalize($("#employee-search").value.trim());
            const department = $("#department-filter").value;
            const job = $("#job-filter").value;
            const status = $("#employee-status-filter").value;
            const records = state.employees.filter(item =>
                normalize(item.id + " " + item.name).includes(query) &&
                (!department || item.department === department) &&
                (!job || item.job === job) && (!status || item.status === status));
            const offset = (selectedPage - 1) * 4;
            $("#employee-rows").innerHTML = records.slice(offset, offset + 4).map(item =>
                '<tr><td><a class="cc-id" href="' + url(item.id + "/") + '">' + escape(item.id) + '</a></td><td><a href="' + url(item.id + "/") + '">' + escape(item.name) + "</a></td><td>" + escape(item.department) + "</td><td>" + escape(item.job) + "</td><td>" + date(item.start_date) + "</td><td>" + statusBadge(item.status) + "</td><td>" + actions(item, "employee") + "</td></tr>"
            ).join("") || '<tr><td colspan="7" class="cc-empty">' + (state.employees.length ? 'Không tìm thấy nhân viên phù hợp với điều kiện lọc.' : 'Chưa có hồ sơ nhân viên. Chọn “Thêm nhân viên” để bắt đầu.') + '</td></tr>';
            $("#employee-count").textContent = records.length ? "Hiển thị " + (offset + 1) + " - " + Math.min(offset + 4, records.length) + " trong " + records.length + " nhân viên" : "Không có nhân viên";
            paginate($("#employee-pagination"), records.length, selectedPage, number => { selectedPage = number; render(); });
        }
        ["employee-search", "department-filter", "job-filter", "employee-status-filter"].forEach(id => {
            $("#" + id).addEventListener(id === "employee-search" ? "input" : "change", () => { selectedPage = 1; render(); });
        });
        render();
    }
    // Cùng một biểu mẫu cho thêm và sửa; mã trang quyết định điền bản ghi nào và gửi đến địa chỉ nào.
    function initEmployeeForm() {
        const form = $("#employee-form");
        const editing = page === "employee-edit";
        const item = editing ? employee(recordId) : null;
        if (editing && !item) { missing(form, "hồ sơ nhân viên"); return; }
        form.elements.department.innerHTML = options(state.departments, "Chọn phòng ban");
        $("#job-options").innerHTML = options(state.jobs, null);
        form.elements.birth_date.max = today();
        if (editing) {
            $("#employee-form-title").textContent = "Chỉnh sửa hồ sơ nhân viên";
            $("#employee-form-description").textContent = "Cập nhật thông tin hồ sơ nhân viên";
            $("#employee-submit").textContent = "Cập nhật hồ sơ";
            Object.entries(item).forEach(([name, value]) => { if (form.elements[name]) form.elements[name].value = value; });
        }
        // Dừng cách gửi biểu mẫu mặc định, gom các ô thành bộ tên/giá trị chuỗi và kiểm tra nhanh trước khi gửi.
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const input = Object.fromEntries(new FormData(form));
            Object.keys(input).forEach(key => { input[key] = input[key].trim(); });
            if (!input.name) { error(form, "Vui lòng nhập họ và tên."); return; }
            if (input.birth_date && input.birth_date >= today()) { error(form, "Ngày sinh phải trước ngày hiện tại."); return; }
            if (input.birth_date && input.start_date < input.birth_date) { error(form, "Ngày vào làm phải sau ngày sinh."); return; }
            if (item?.end_date && input.start_date > item.end_date) { error(form, "Ngày vào làm không được sau ngày nghỉ việc."); return; }
            const other = state.employees.filter(entry => entry.id !== item?.id);
            if (other.some(entry => entry.identity === input.identity)) { error(form, "Số CCCD đã được sử dụng trong một hồ sơ khác."); return; }
            if (other.some(entry => entry.email.toLowerCase() === input.email.toLowerCase())) { error(form, "Email đã được sử dụng trong một hồ sơ khác."); return; }
            await submit(form, "api/employees/" + (editing ? item.id + "/" : ""), input, "");
        });
        form.addEventListener("input", () => { $(".cc-form-error", form).hidden = true; });
    }
    function definition(rows, className = "cc-definition") {
        const grouped = className.includes("cc-personal-fields");
        return '<dl class="' + className + '">' + rows.map(([label, value]) => (grouped ? "<div>" : "") + "<dt>" + escape(label) + "</dt><dd>" + escape(value || "—") + "</dd>" + (grouped ? "</div>" : "")).join("") + "</dl>";
    }
    // Chọn hợp đồng đang hiệu lực, nếu không có dùng bản mới nhất; nhãn Hợp đồng hiện tại không bảo đảm luôn có hợp đồng hiệu lực.
    function renderEmployeeDetail() {
        const item = employee(recordId);
        const target = $("#employee-detail-content");
        if (!item) { missing(target, "hồ sơ nhân viên"); return; }
        $("#employee-detail-actions").innerHTML = '<a class="cc-button cc-button-secondary" href="' + url(item.id + "/edit/") + '">Chỉnh sửa</a>' +
            (item.status === "active" ? '<button class="cc-button cc-button-danger" type="button" data-deactivate="' + escape(item.id) + '">Vô hiệu hóa</button>' : "");
        const contracts = state.contracts.filter(contract => contract.employee_id === item.id).sort((a,b) => b.start_date.localeCompare(a.start_date));
        const current = contracts.find(contract => ["active", "expiring"].includes(contractStatus(contract))) || contracts[0];
        target.innerHTML = '<section class="cc-panel cc-profile-banner"><span class="cc-profile-avatar">' + icon('user') + '</span><div><h2>' + escape(item.name) + '</h2><span class="cc-id">' + escape(item.id) + "</span>" + statusBadge(item.status) + '</div><div class="cc-banner-job"><strong>' + escape(item.job) + "</strong><p>" + escape(item.department) + '</p></div></section><section class="cc-panel cc-details-panel"><div><h2>Thông tin cá nhân</h2>' +
            definition([["Họ và tên",item.name],["Ngày sinh",date(item.birth_date)],["Giới tính",item.gender],["CCCD",item.identity],["Số điện thoại",item.phone],["Email",item.email],["Địa chỉ",item.address]]) +
            '</div><div><h2>Thông tin công việc</h2>' + definition([["Phòng ban",item.department],["Chức vụ",item.job],["Ngày vào làm",date(item.start_date)],["Trạng thái",item.status === "active" ? "Đang làm việc" : "Đã nghỉ việc"],["Ngày nghỉ việc",date(item.end_date)],["Lý do nghỉ việc",item.reason]]) + '</div></section><section class="cc-panel cc-current-contract"><h2>Hợp đồng hiện tại</h2><div><div>' +
            (current ? '<strong>' + escape(current.type) + "</strong><p>" + date(current.start_date) + " → " + (current.end_date ? date(current.end_date) : "Không xác định thời hạn") + '</p></div><a class="cc-button cc-button-secondary" href="' + url("contracts/" + current.id + "/") + '">Xem hợp đồng</a>' : '<p>Chưa có hợp đồng lao động.</p></div>') + "</div></section>";
    }
    // Hộp xác nhận chỉ thu ngày và lý do; API mới là nơi đổi trạng thái hồ sơ và khóa tài khoản.
    function initDeactivate() {
        const dialog = $("#deactivate-dialog");
        const form = $("#deactivate-form");
        let selectedId = null;
        document.addEventListener("click", event => {
            const button = event.target.closest("[data-deactivate]");
            if (!button) return;
            const item = employee(button.dataset.deactivate);
            if (!item || item.status !== "active") return;
            const actionsMenu = button.closest(".cc-actions");
            if (actionsMenu) actionsMenu.open = false;
            selectedId = item.id;
            form.reset();
            form.elements.end_date.value = today();
            form.elements.end_date.min = item.start_date;
            form.elements.end_date.max = today();
            $(".cc-form-error", form).hidden = true;
            $("#deactivate-description").textContent = "Bạn có chắc muốn chuyển " + item.name + " (" + item.id + ') sang trạng thái “Đã nghỉ việc”?';
            dialog.showModal();
        });
        $("[data-close-dialog]").addEventListener("click", () => { dialog.close(); });
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const item = employee(selectedId);
            const values = Object.fromEntries(new FormData(form));
            if (!item || !values.reason.trim()) { error(form, "Vui lòng nhập lý do nghỉ việc."); return; }
            if (values.end_date < item.start_date || values.end_date > today()) { error(form, "Ngày nghỉ việc phải từ ngày vào làm đến ngày hiện tại."); return; }
            await submit(form, "api/employees/" + item.id + "/deactivate/", values, "");
        });
    }
    // Dùng trạng thái đã tính trên máy chủ để lọc, đếm cảnh báo và trình bày danh sách hợp đồng.
    function initContractList() {
        let selectedPage = 1;
        $("#contract-type-filter").innerHTML = options(state.types, "Loại hợp đồng");
        $("#contract-status-filter").insertAdjacentHTML("beforeend", '<option value="upcoming">Chưa hiệu lực</option><option value="terminated">Chấm dứt</option>');
        $("#contract-search").value = new URLSearchParams(location.search).get("q") || "";
        const expiringCount = state.contracts.filter(item => contractStatus(item) === "expiring").length;
        $("#expiry-count").textContent = expiringCount + " hợp đồng sắp hết hạn trong 30 ngày";
        $("#expiry-alert").hidden = !expiringCount;
        function render() {
            const query = normalize($("#contract-search").value.trim());
            const type = $("#contract-type-filter").value;
            const status = $("#contract-status-filter").value;
            const records = state.contracts.filter(item => normalize(item.id + " " + (employee(item.employee_id)?.name || "")).includes(query) &&
                (!type || item.type === type) && (!status || contractStatus(item) === status));
            const offset = (selectedPage - 1) * 4;
            $("#contract-rows").innerHTML = records.slice(offset, offset + 4).map(item =>
                '<tr><td><a class="cc-id" href="' + url("contracts/" + item.id + "/") + '">' + escape(item.id) + '</a></td><td><a href="' + url(item.employee_id + "/") + '">' + escape(employee(item.employee_id)?.name || "—") + "</a></td><td>" + escape(item.type) + "</td><td>" + date(item.start_date) + "</td><td>" + date(item.end_date) + "</td><td>" + statusBadge(contractStatus(item), true) + "</td><td>" + actions(item, "contract") + "</td></tr>"
            ).join("") || '<tr><td colspan="7" class="cc-empty">' + (state.contracts.length ? 'Không tìm thấy hợp đồng phù hợp với điều kiện lọc.' : 'Chưa có hợp đồng. Thêm hồ sơ nhân viên rồi chọn “Tạo hợp đồng”.') + '</td></tr>';
            $("#contract-count").textContent = records.length ? "Hiển thị " + (offset + 1) + " - " + Math.min(offset + 4, records.length) + " trong " + records.length + " hợp đồng" : "Không có hợp đồng";
            paginate($("#contract-pagination"), records.length, selectedPage, number => { selectedPage = number; render(); });
        }
        ["contract-search", "contract-type-filter", "contract-status-filter"].forEach(id => {
            $("#" + id).addEventListener(id === "contract-search" ? "input" : "change", () => { selectedPage = 1; render(); });
        });
        $("#view-expiring").addEventListener("click", () => { $("#contract-status-filter").value = "expiring"; selectedPage = 1; render(); $("#contract-status-filter").focus(); });
        render();
    }
    function field(label, name, type = "text", value = "", required = false, readOnly = false, placeholder = "") {
        return '<label class="cc-field">' + escape(label) + (required ? " <span>*</span>" : "") + '<input name="' + name + '" type="' + type + '" value="' + escape(value) + '"' + (required ? " required" : "") + (readOnly ? " readonly" : "") + (placeholder ? ' placeholder="' + escape(placeholder) + '"' : "") + (type === "number" ? ' min="0.01" step="0.01"' : "") + "></label>";
    }
    function selectField(label, name, values, firstLabel, value = "") {
        return '<label class="cc-field">' + escape(label) + ' <span>*</span><select name="' + name + '" required>' + options(values, firstLabel, value) + "</select></label>";
    }
    // Tạo mới cho nhập các thông tin gốc; gia hạn chỉ cho nhập ngày/lương, máy chủ cũng giới hạn các trường này.
    function initContractForm() {
        const form = $("#contract-form");
        const editing = page === "contract-edit";
        const item = editing ? state.contracts.find(entry => entry.id === recordId) : null;
        if (editing && !item) { missing(form, "hợp đồng", "contracts/"); return; }
        if (editing) {
            $("#contract-form-title").textContent = "Chỉnh sửa / Gia hạn hợp đồng";
            $("#contract-form-description").textContent = "Chỉnh sửa / gia hạn hợp đồng lao động";
            $("#contract-submit").textContent = "Cập nhật hợp đồng";
            $("#contract-fields").innerHTML = '<div class="cc-form-grid">' +
                field("Mã hợp đồng", "id", "text", item.id, false, true) +
                field("Nhân viên", "employee_label", "text", item.employee_id + " - " + (employee(item.employee_id)?.name || ""), false, true) +
                field("Loại hợp đồng", "type", "text", item.type, false, true) +
                field("Ngày gia hạn", "renewal_date", "date", item.renewal_date || "") +
                field("Ngày hết hạn mới", "end_date", "date", item.end_date, item.type !== "Không xác định thời hạn") +
                field("Lương cơ bản mới (VNĐ)", "salary", "number", item.salary, true) + "</div>";
            form.elements.end_date.min = item.start_date;
            if (item.type === "Không xác định thời hạn") form.elements.end_date.disabled = true;
        } else {
            const selectable = state.employees.filter(entry => entry.status === "active");
            $("#contract-fields").innerHTML = '<div class="cc-form-grid"><label class="cc-field">Nhân viên <span>*</span><select name="employee_id" required><option value="">Chọn nhân viên</option>' +
                selectable.map(entry => '<option value="' + escape(entry.id) + '">' + escape(entry.id + " - " + entry.name) + "</option>").join("") + "</select></label>" +
                selectField("Loại hợp đồng", "type", state.creationTypes, "Chọn loại hợp đồng") + '</div><div class="cc-three-column">' +
                field("Ngày ký", "signed_date", "date", "", true) + field("Ngày bắt đầu", "start_date", "date", "", true) + field("Ngày hết hạn", "end_date", "date") +
                '</div><div class="cc-salary">' + field("Lương cơ bản (VNĐ)", "salary", "number", "", true, false, "Nhập lương cơ bản") + "</div>";
            form.elements.type.addEventListener("change", () => {
                const indefinite = form.elements.type.value === "Không xác định thời hạn";
                form.elements.end_date.disabled = indefinite;
                form.elements.end_date.required = !indefinite;
                if (indefinite) form.elements.end_date.value = "";
            });
            form.elements.start_date.addEventListener("change", () => { form.elements.end_date.min = form.elements.start_date.value; });
        }
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const input = Object.fromEntries(new FormData(form));
            const salary = Number(input.salary);
            if (!Number.isFinite(salary) || salary <= 0 || !/^\d+(\.\d{1,2})?$/.test(input.salary)) { error(form, "Lương cơ bản phải lớn hơn 0 và có tối đa 2 chữ số thập phân."); return; }
            const start = editing ? item.start_date : input.start_date;
            const type = editing ? item.type : input.type;
            const end = type === "Không xác định thời hạn" ? "" : input.end_date;
            if (type !== "Không xác định thời hạn" && (!end || end <= start)) { error(form, "Ngày hết hạn phải sau ngày bắt đầu."); return; }
            if (editing && input.renewal_date && (input.renewal_date < start || (end && input.renewal_date > end))) { error(form, "Ngày gia hạn phải nằm trong thời gian hiệu lực của hợp đồng."); return; }
            if (!editing && input.signed_date > start) { error(form, "Ngày ký không được sau ngày bắt đầu hợp đồng."); return; }
            if (!editing) {
                const person = employee(input.employee_id);
                if (!person || person.status !== "active") { error(form, "Vui lòng chọn nhân viên đang làm việc."); return; }
                // Kiểm tra nhanh hai khoảng ngày có giao nhau; hợp đồng chấm dứt không chặn một hợp đồng mới.
                if (state.contracts.some(entry => entry.status !== "terminated" && entry.employee_id === person.id &&
                    (!entry.end_date || entry.end_date >= start) && (!end || entry.start_date <= end))) {
                    error(form, "Khoảng thời gian này trùng với một hợp đồng của nhân viên."); return;
                }
            } else {
                if (state.contracts.some(entry => entry.status !== "terminated" && entry.id !== item.id && entry.employee_id === item.employee_id &&
                    (!entry.end_date || entry.end_date >= start) && (!end || entry.start_date <= end))) {
                    error(form, "Khoảng thời gian mới trùng với một hợp đồng khác của nhân viên."); return;
                }
            }
            await submit(form, "api/contracts/" + (editing ? item.id + "/" : ""), input, "contracts/");
        });
        form.addEventListener("input", () => { $(".cc-form-error", form).hidden = true; });
    }
    // Dùng lại cách dựng chi tiết cho Quản lý và Nhân viên; chính sách chưa có dữ liệu sẽ hiện Chưa cập nhật.
    function contractContent(item, own = false) {
        const person = employee(item.employee_id);
        const status = contractStatus(item);
        const range = date(item.start_date) + " – " + (item.end_date ? date(item.end_date) : "Không xác định thời hạn");
        const rows = [["Mã hợp đồng", item.id], ["Người lao động", (own ? "" : item.employee_id + " · ") + (person?.name || "—")], ["Vị trí công việc", person?.job], ["Loại hợp đồng", item.type], ["Ngày ký", date(item.signed_date)], ["Ngày bắt đầu", date(item.start_date)], ["Ngày hết hạn", date(item.end_date)], ["Ngày gia hạn", item.renewal_date ? date(item.renewal_date) : "Chưa gia hạn"], ["Lương cơ bản", money(item.salary)]];
        const statusText = {active:"Đang hiệu lực",expiring:"Sắp hết hạn",expired:"Đã hết hạn",upcoming:"Chưa hiệu lực",terminated:"Chấm dứt"}[status];
        return '<section class="cc-contract-summary"><div class="cc-contract-identity"><span class="cc-icon-tile cc-pink-icon">' + icon("file") + '</span><div><small>HỢP ĐỒNG LAO ĐỘNG</small><h2>' + escape(item.id) + "</h2>" + statusBadge(status,true) +
            '</div></div><div><p class="cc-muted">Loại hợp đồng</p><p>' + escape(item.type) + '</p></div><div><p class="cc-muted">Thời gian hiệu lực</p><p>' + escape(range) + '</p></div></section><div class="cc-contract-detail-grid"><section class="cc-contract-card"><h2><span class="cc-small-tile cc-pink-icon">' + icon("file") + '</span>Chi tiết hợp đồng</h2><dl class="cc-contract-definition">' +
            rows.map(([label,value]) => "<div><dt>" + escape(label) + "</dt><dd>" + escape(value || "—") + "</dd></div>").join("") +
            '<div><dt>Trạng thái</dt><dd class="' + (status === "active" ? "cc-green-text" : "") + '">' + escape(statusText) + '</dd></div></dl></section><aside class="cc-contract-card"><h2><span class="cc-small-tile cc-pink-icon">' + icon("shield") + '</span>Chính sách áp dụng</h2><dl class="cc-policy"><dt>Người sử dụng lao động</dt><dd>Chưa cập nhật</dd><dt>Địa điểm làm việc</dt><dd>Chưa cập nhật</dd><dt>Thời giờ làm việc</dt><dd>Chưa cập nhật</dd><dt>Ngày nghỉ &amp; phép năm</dt><dd>Chưa cập nhật</dd><dt>Bảo hiểm</dt><dd>Chưa cập nhật</dd>' +
            (own ? '<dt>Phụ cấp áp dụng</dt><dd>Chưa cập nhật</dd>' : "") + "</dl></aside></div>";
    }
    function renderContractDetail() {
        const item = state.contracts.find(entry => entry.id === recordId);
        if (!item) { missing($("#contract-detail-content"), "hợp đồng", "contracts/"); return; }
        $("#contract-detail-actions").innerHTML = statusBadge(contractStatus(item),true) + '<a class="cc-button cc-button-primary" href="' + url("contracts/" + item.id + "/edit/") + '">Chỉnh sửa / Gia hạn</a>';
        $("#contract-detail-content").innerHTML = contractContent(item);
    }
    // Chỉ các hợp đồng của currentUser được trình bày; máy chủ đã giới hạn dữ liệu trước bước này.
    function renderMyContracts() {
        const records = state.contracts.filter(item => item.employee_id === currentUser?.id).sort((a,b) => b.start_date.localeCompare(a.start_date));
        if (!records.length) {
            $("#my-contract-content").innerHTML = '<section class="cc-panel cc-empty-panel"><h2>Chưa có hợp đồng lao động</h2><p>Hợp đồng của bạn sẽ hiển thị tại đây khi được cập nhật.</p></section>';
            return;
        }
        const select = $("#my-contract-select");
        select.hidden = records.length < 2;
        select.innerHTML = records.map(item => '<option value="' + escape(item.id) + '">' + escape(item.id + " · " + date(item.start_date)) + "</option>").join("");
        function render() { $("#my-contract-content").innerHTML = contractContent(records.find(item => item.id === select.value) || records[0], true); }
        select.addEventListener("change", render);
        render();
    }
    // Hồ sơ cá nhân lấy từ liên kết tài khoản; chưa liên kết thì hiện trạng thái rỗng, không gán một nhân viên mẫu.
    function renderMyProfile() {
        const person = currentUser;
        if (!person) {
            $("#my-profile-content").innerHTML = '<section class="cc-panel cc-empty-panel"><h2>Chưa có hồ sơ nhân viên</h2><p>Tài khoản của bạn chưa được liên kết với hồ sơ. Người quản lý có thể liên kết tại trang quản trị.</p><a class="cc-button cc-button-secondary" href="' + escape(body.dataset.passwordUrl) + '">Đổi mật khẩu</a></section>';
            return;
        }
        const displayJob = person.job;
        const personal = [["Họ và tên", person.name],["Ngày sinh",date(person.birth_date)],["Giới tính",person.gender],["CCCD",person.identity],["Số điện thoại",person.phone],["Email",person.email]];
        $("#my-profile-content").innerHTML = '<section class="cc-personal-banner"><div class="cc-user-card"><span class="cc-avatar">' + escape(seed.account.initials) + '</span><div><h2>' + escape(person.name) + "</h2><p>" + escape(displayJob + " · " + person.id) + "</p>" + statusBadge(person.status) +
            '</div></div><div><small>BỘ PHẬN</small><h3>' + escape(person.department) + '</h3><p>Cake Crush</p></div><div><small>NGÀY GIA NHẬP</small><h3>' + date(person.start_date) +
            '</h3><p>Thành viên Cake Crush</p></div></section><div class="cc-personal-columns"><div><section class="cc-personal-card"><h2><span class="cc-small-tile">' + icon("user") +
            '</span>Thông tin cá nhân</h2><dl class="cc-personal-fields">' + personal.map(([label,value]) => "<div><dt>" + escape(label) + "</dt><dd>" + escape(value || "—") + "</dd></div>").join("") +
            '</dl></section><section class="cc-personal-card"><h2><span class="cc-small-tile cc-pink-icon">' + icon("map-pin") + '</span>Địa chỉ liên hệ</h2><p class="cc-muted">Địa chỉ hiện tại</p><p>' + escape(person.address) +
            '</p></section></div><div><section class="cc-personal-card"><h2><span class="cc-small-tile cc-pink-icon">' + icon("briefcase") + '</span>Thông tin công việc</h2>' +
            definition([["Mã nhân viên",person.id],["Bộ phận",person.department],["Chức vụ",displayJob]], "cc-personal-fields cc-work-fields") +
            '<p class="cc-green-text">Thông tin do bộ phận nhân sự quản lý</p></section><section class="cc-personal-card cc-security"><span class="cc-small-tile cc-pink-icon">' + icon("lock") +
            '</span><div><h3>Bảo mật tài khoản</h3><p>Cập nhật mật khẩu để bảo vệ thông tin.</p><button type="button" class="cc-link-button" id="password-change">Đổi mật khẩu →</button></div></section></div></div>';
        $("#password-change").addEventListener("click", () => { location.assign(body.dataset.passwordUrl); });
    }

    initShell();
    initDeactivate();
    // Bảng chọn hàm theo data-page nối từng trang HTML với phần xử lý tương ứng.
    const handlers = {
        "employee-list": initEmployeeList,
        "employee-create": initEmployeeForm,
        "employee-edit": initEmployeeForm,
        "employee-detail": renderEmployeeDetail,
        "contract-list": initContractList,
        "contract-create": initContractForm,
        "contract-edit": initContractForm,
        "contract-detail": renderContractDetail,
        "my-profile": renderMyProfile,
        "my-contracts": renderMyContracts,
    };
    if (handlers[page]) handlers[page]();
})();
