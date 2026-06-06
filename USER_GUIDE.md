2. How the Flow Works (User Experience)Owner registers → Creates first Company → Automatically becomes OWNER of that company.
Owner logs in → Sees company selector (if they have >1 company).
After selecting company → All the app works in that company context.
HR / Employee same thing — they can switch companies via a nice dropdown in the navbar.

The system hierarchy is structured as follows:

**Root/Admin → Company Owners → HR → Employees**

However, users are not limited to a single company. The platform should support multi-company relationships at every level:

* A **Company Owner** can own multiple companies.
* An **HR user** can manage multiple companies.
* An **Employee** can work for multiple companies.

### Role Responsibilities

* **Root/Admin**

  * Manages the entire platform.
  * Has full system-level access.

* **Company Owners**

  * Create and manage HR accounts for their companies.
  * Configure company settings and access.

* **HR**

  * Create and manage employee accounts.
  * Handle employee-related operations within assigned companies.

* **Employees**

  * Access only their own company-related information and functions.

### Authentication and Company Selection

Each user should register with a personal email address. This email will be used for:

* Login authentication
* Password reset and account recovery
* Security notifications

A more secure approach could also include:

* Email verification during registration
* Optional two-factor authentication (2FA)
* Password reset links with expiration tokens

### Multi-Company Workflow

When a Company Owner creates an account, they should specify which companies will use the platform.

After login:

* If the user belongs to only one company, the app opens directly into that company workspace.
* If the user belongs to multiple companies, the system should prompt them to select the company they want to work with.

This behavior applies to:

* Company Owners
* HR users
* Employees

Once inside the application, users should be able to switch between companies easily using a company selector dropdown in the interface. Think of it like changing “workspaces” instead of logging out and back in every time. A tiny air-traffic-control tower for payroll ✈️📋

### Suggested Improvements

A few architectural ideas that could make the system cleaner and more scalable:

* Use a **many-to-many relationship** between Users and Companies.
* Store roles per company membership instead of globally.

  * Example:

    * Teo = HR in Company A
    * Teo = Employee in Company B
* Create a `Membership` or `CompanyUser` table with:

  * user
  * company
  * role
  * status
  * permissions

This approach gives you flexibility for future growth and avoids role conflicts later.
