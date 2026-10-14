import re

with open('template/register.html', 'r', encoding='utf-8') as f:
    data = f.read()

# Add ID to form
data = data.replace('<form action="/register" method="POST" class="space-y-5">', '<form id="registerForm" action="/register" method="POST" class="space-y-5">')

# Remove checkbox and change submit button
old_button_area = r'''            <div class="flex items-start pt-2">
                <div class="flex items-center h-5">
                    <input id="terms" name="terms" type="checkbox" required class="focus:ring\[#668054\] h-4 w-4 text-\[#668054\] border-gray-300 rounded cursor-pointer">
                </div>
                <div class="ml-3 text-sm">
                    <label for="terms" class="text-gray-600 cursor-pointer">I agree to the <a href="/terms" target="_blank" class="text-\[#668054\] hover:underline font-medium">Terms of Agreement</a> and <a href="/privacy" target="_blank" class="text-\[#668054\] hover:underline font-medium">Privacy Policy</a>\.</label>
                </div>
            </div>

            <div class="pt-2">
                <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-\[#668054\] hover:bg-\[#829c74\] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-\[#668054\] transition-colors">
                    Register Account
                </button>
            </div>'''

new_button_area = '''            <div class="pt-2">
                <button type="button" onclick="openPrivacyModal()" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#668054] hover:bg-[#829c74] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#668054] transition-colors">
                    Register Account
                </button>
            </div>'''

data = re.sub(old_button_area, new_button_area, data)

# Add Modal HTML at the end before </body> or just at the end of the file
modal_html = '''
    <!-- Privacy & Terms Modal -->
    <div id="privacyModal" class="fixed inset-0 z-[100] hidden">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onclick="closePrivacyModal()"></div>
        
        <!-- Modal Content -->
        <div class="fixed inset-0 z-10 overflow-y-auto">
            <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
                <div class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-2xl flex flex-col max-h-[85vh]">
                    
                    <!-- Header -->
                    <div class="bg-white px-6 py-4 border-b border-gray-100 flex items-center justify-between shrink-0">
                        <div class="flex items-center gap-3">
                            <div class="flex-shrink-0 bg-green-500 rounded-lg p-2 text-white shadow-sm">
                                <i class="fa-solid fa-shield-halved text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-lg font-bold text-gray-900 leading-tight">Privacy Notice & Terms of Use</h3>
                                <p class="text-xs text-gray-500 font-medium">CCA Exam Management System</p>
                            </div>
                        </div>
                        <button type="button" onclick="closePrivacyModal()" class="text-gray-400 hover:text-gray-500 focus:outline-none bg-gray-50 hover:bg-gray-100 rounded-full p-2 transition-colors">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                    
                    <!-- Scrollable Body -->
                    <div id="privacyScrollArea" class="px-8 py-6 overflow-y-auto flex-1 relative">
                        <!-- Warning Banner -->
                        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-6 flex items-center justify-center text-yellow-800 text-sm font-medium shadow-sm">
                            Please read and scroll through this notice before registering.
                        </div>

                        <div class="space-y-6 text-sm text-gray-600">
                            <div>
                                <h4 class="font-bold text-gray-900 mb-2">1. Data Collection</h4>
                                <p class="mb-2">The CCA Exam Management System collects the following personal information:</p>
                                <ul class="list-disc pl-5 space-y-1 text-gray-600">
                                    <li>Full name and account type</li>
                                    <li>CCA Email Address</li>
                                    <li>Section and Institute details</li>
                                </ul>
                            </div>

                            <div>
                                <h4 class="font-bold text-gray-900 mb-2">2. Purpose of Collection</h4>
                                <p class="mb-2">Your information is collected for the following purposes:</p>
                                <ul class="list-disc pl-5 space-y-1 text-gray-600">
                                    <li>To verify your identity within the CCA community</li>
                                    <li>To manage and generate personalized exam timetables</li>
                                    <li>To prevent scheduling conflicts and secure system access</li>
                                </ul>
                            </div>

                            <div>
                                <h4 class="font-bold text-gray-900 mb-2">3. Data Storage & Security</h4>
                                <p>All data is securely stored using a cloud platform complying with international data security standards. Access is restricted to authorized CCA personnel. Your data is never sold or shared with third parties.</p>
                            </div>

                            <div>
                                <h4 class="font-bold text-gray-900 mb-2">4. User Responsibilities</h4>
                                <p>You are responsible for maintaining the confidentiality of your account. Any fraudulent activity or attempt to alter exam schedules without authorization is strictly prohibited and subject to disciplinary action.</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="bg-white px-8 py-5 border-t border-gray-100 flex flex-col items-center shrink-0">
                        <p id="scrollHint" class="text-xs text-gray-500 mb-3 font-medium transition-colors">Please scroll through the entire notice to continue.</p>
                        <button type="button" id="agreeBtn" disabled onclick="submitRegistration()" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-gray-300 cursor-not-allowed transition-all duration-300">
                            I Agree & Continue
                        </button>
                        <p class="text-[10px] text-gray-400 mt-3">Data Privacy Act of 2012 - Republic Act No. 10173</p>
                    </div>
                    
                </div>
            </div>
        </div>
    </div>

    <script>
        const modal = document.getElementById('privacyModal');
        const scrollArea = document.getElementById('privacyScrollArea');
        const agreeBtn = document.getElementById('agreeBtn');
        const scrollHint = document.getElementById('scrollHint');
        const form = document.getElementById('registerForm');

        function openPrivacyModal() {
            if (form.reportValidity()) {
                modal.classList.remove('hidden');
                // Reset scroll
                scrollArea.scrollTop = 0;
                checkScroll();
            }
        }

        function closePrivacyModal() {
            modal.classList.add('hidden');
        }

        function checkScroll() {
            // Check if user has scrolled to the bottom (with a 2px margin for rounding errors)
            if (scrollArea.scrollHeight - scrollArea.scrollTop <= scrollArea.clientHeight + 2) {
                agreeBtn.disabled = false;
                agreeBtn.classList.remove('bg-gray-300', 'cursor-not-allowed');
                agreeBtn.classList.add('bg-[#668054]', 'hover:bg-[#4b5e3d]', 'cursor-pointer', 'shadow-md');
                scrollHint.classList.add('text-transparent'); // Hide text but keep space
            }
        }

        scrollArea.addEventListener('scroll', checkScroll);

        function submitRegistration() {
            if (!agreeBtn.disabled) {
                form.submit();
            }
        }
    </script>
'''

data = data.replace('</body>', modal_html + '\n</body>')

with open('template/register.html', 'w', encoding='utf-8') as f:
    f.write(data)
