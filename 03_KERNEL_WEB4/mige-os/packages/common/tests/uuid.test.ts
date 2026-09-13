import { UUID } from '../src/uuid';

describe('UUID', () => {
  describe('v4', () => {
    it('should generate valid UUID v4', () => {
      const uuid = UUID.v4();
      expect(UUID.isValid(uuid)).toBe(true);
    });

    it('should generate unique UUIDs', () => {
      const uuid1 = UUID.v4();
      const uuid2 = UUID.v4();
      expect(uuid1).not.toBe(uuid2);
    });

    it('should generate UUID with correct format', () => {
      const uuid = UUID.v4();
      expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
  });

  describe('v5', () => {
    it('should generate deterministic UUID v5', () => {
      const uuid1 = UUID.v5('namespace', 'name');
      const uuid2 = UUID.v5('namespace', 'name');
      expect(uuid1).toBe(uuid2);
    });

    it('should generate different UUIDs for different names', () => {
      const uuid1 = UUID.v5('namespace', 'name1');
      const uuid2 = UUID.v5('namespace', 'name2');
      expect(uuid1).not.toBe(uuid2);
    });
  });

  describe('isValid', () => {
    it('should validate valid UUID', () => {
      const validUuid = '550e8400-e29b-41d4-a716-446655440000';
      expect(UUID.isValid(validUuid)).toBe(true);
    });

    it('should reject invalid UUID', () => {
      const invalidUuid = 'not-a-uuid';
      expect(UUID.isValid(invalidUuid)).toBe(false);
    });

    it('should reject UUID with wrong version', () => {
      const invalidVersion = '550e8400-e29b-61d4-a716-446655440000';
      expect(UUID.isValid(invalidVersion)).toBe(false);
    });
  });
});